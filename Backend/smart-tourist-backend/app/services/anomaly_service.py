"""
Heuristic Anomaly Detection Engine

This service implements rule-based anomaly detection for tourist safety:
- Inactivity detection (tourists inactive for > 60 minutes)
- Route deviation detection (deviation from planned itinerary)
- High-risk zone detection (geo-fencing for dangerous areas)

The service runs as a background task, periodically analyzing all active tourists
and integrating with existing alert and ledger services.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from shapely.geometry import Point, LineString
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.db import models
from app.crud import crud_tourist, crud_dashboard
from app.services import alert_service, ledger_service, ml_anomaly_service


# Configuration constants
INACTIVITY_THRESHOLD_MINUTES = 60
ROUTE_DEVIATION_THRESHOLD_METERS = 500  # 500 meters from planned route
BACKGROUND_TASK_INTERVAL_SECONDS = 60  # Run checks every minute


def check_inactivity(db: Session, tourist: models.Tourist) -> None:
    """
    Check if a tourist has been inactive for longer than the threshold.
    
    Args:
        db: Database session
        tourist: Tourist model instance
        
    Triggers:
        - Inactivity alert via alert_service
        - Anomaly event log via ledger_service
    """
    # Get the latest location log for this tourist
    latest_location = crud_tourist.get_latest_location_by_tourist_id(db, tourist.id)
    
    if not latest_location:
        # No location data - this is also an anomaly
        print(f"⚠️  No location data found for tourist {tourist.id}")
        return
    
    # Calculate time since last location update
    time_since_last_update = datetime.utcnow() - latest_location.timestamp
    
    if time_since_last_update > timedelta(minutes=INACTIVITY_THRESHOLD_MINUTES):
        print(f"🚨 Inactivity detected for tourist {tourist.id}: {time_since_last_update}")
        
        # Trigger inactivity alert
        alert_service.trigger_inactivity_alert(
            db=db,
            tourist_id=tourist.id,
            last_seen_location={"latitude": latest_location.latitude, "longitude": latest_location.longitude},
            minutes_inactive=int(time_since_last_update.total_seconds() / 60)
        )
        
        # Log anomaly event to ledger
        ledger_service.log_anomaly_event_to_ledger(
            db=db,
            tourist_id=tourist.id,
            anomaly_type="INACTIVITY",
            details={
                "last_location": {
                    "latitude": latest_location.latitude,
                    "longitude": latest_location.longitude,
                    "timestamp": latest_location.timestamp.isoformat()
                },
                "minutes_inactive": int(time_since_last_update.total_seconds() / 60),
                "threshold_minutes": INACTIVITY_THRESHOLD_MINUTES
            }
        )


def check_route_deviation(db: Session, tourist: models.Tourist, latest_location: models.LocationLog) -> None:
    """
    Check if a tourist has deviated significantly from their planned itinerary.
    
    Args:
        db: Database session
        tourist: Tourist model instance
        latest_location: Latest location log entry
        
    Triggers:
        - Location alert via alert_service
        - Anomaly event log via ledger_service
    """
    # Get the tourist's itinerary points ordered by sequence
    itinerary_points = db.query(models.TouristItinerary).filter(
        models.TouristItinerary.tourist_id == tourist.id
    ).order_by(models.TouristItinerary.sequence_order).all()
    
    if len(itinerary_points) < 2:
        # Need at least 2 points to create a route
        return
    
    # Convert itinerary points to a LineString
    coordinates = []
    for point in itinerary_points:
        # Convert PostGIS geometry to shapely geometry
        shapely_point = to_shape(point.location)
        coordinates.append((shapely_point.x, shapely_point.y))
    
    planned_route = LineString(coordinates)
    
    # Create point for current location
    current_point = Point(latest_location.longitude, latest_location.latitude)
    
    # Calculate distance from current location to planned route
    distance_meters = planned_route.distance(current_point) * 111000  # Rough conversion to meters
    
    if distance_meters > ROUTE_DEVIATION_THRESHOLD_METERS:
        print(f"🚨 Route deviation detected for tourist {tourist.id}: {distance_meters:.0f}m from planned route")
        
        # Trigger location alert
        alert_service.trigger_location_alert(
            db=db,
            tourist_id=tourist.id,
            current_location={"latitude": latest_location.latitude, "longitude": latest_location.longitude},
            alert_type="ROUTE_DEVIATION"
        )
        
        # Log anomaly event to ledger
        ledger_service.log_anomaly_event_to_ledger(
            db=db,
            tourist_id=tourist.id,
            anomaly_type="ROUTE_DEVIATION",
            details={
                "current_location": {
                    "latitude": latest_location.latitude,
                    "longitude": latest_location.longitude,
                    "timestamp": latest_location.timestamp.isoformat()
                },
                "deviation_distance_meters": distance_meters,
                "threshold_meters": ROUTE_DEVIATION_THRESHOLD_METERS,
                "itinerary_points_count": len(itinerary_points)
            }
        )


def check_high_risk_zone(db: Session, tourist: models.Tourist, latest_location: models.LocationLog) -> None:
    """
    Check if a tourist has entered a high-risk zone.
    
    Args:
        db: Database session
        tourist: Tourist model instance
        latest_location: Latest location log entry
        
    Triggers:
        - Location alert via alert_service
        - Anomaly event log via ledger_service
    """
    # Create PostGIS point from current location
    current_point = func.ST_MakePoint(latest_location.longitude, latest_location.latitude)
    
    # Check if current location is within any high-risk zone
    high_risk_zones = db.query(models.HighRiskZone).filter(
        func.ST_Contains(models.HighRiskZone.geometry, current_point)
    ).all()
    
    for zone in high_risk_zones:
        print(f"🚨 High-risk zone entry detected for tourist {tourist.id}: {zone.name}")
        
        # Trigger location alert
        alert_service.trigger_location_alert(
            db=db,
            tourist_id=tourist.id,
            current_location={"latitude": latest_location.latitude, "longitude": latest_location.longitude},
            alert_type="HIGH_RISK_ZONE"
        )
        
        # Log anomaly event to ledger
        ledger_service.log_anomaly_event_to_ledger(
            db=db,
            tourist_id=tourist.id,
            anomaly_type="HIGH_RISK_ZONE",
            details={
                "current_location": {
                    "latitude": latest_location.latitude,
                    "longitude": latest_location.longitude,
                    "timestamp": latest_location.timestamp.isoformat()
                },
                "zone_name": zone.name,
                "zone_id": zone.id
            }
        )


def run_single_tourist_check(db: Session, tourist_id: str) -> None:
    """
    Run all anomaly checks for a single tourist.
    
    Args:
        db: Database session
        tourist_id: UUID of the tourist to check
    """
    # Get tourist details
    tourist = crud_tourist.get_tourist(db, tourist_id)
    if not tourist:
        print(f"❌ Tourist {tourist_id} not found")
        return
    
    # Get latest location for this tourist
    latest_location = crud_tourist.get_latest_location_by_tourist_id(db, tourist_id)
    if not latest_location:
        print(f"📍 No location data for tourist {tourist_id}")
        return
    
    print(f"🔍 Running anomaly checks for tourist {tourist_id}")
    
    # Run all anomaly checks
    try:
        check_inactivity(db, tourist)
        
        if latest_location:  # Additional check since inactivity might not have location
            check_route_deviation(db, tourist, latest_location)
            check_high_risk_zone(db, tourist, latest_location)
            
            # ML-based behavioral anomaly detection
            ml_anomaly = ml_anomaly_service.detect_behavioral_anomalies(db, tourist.id, latest_location)
            if ml_anomaly:
                # Trigger a new, specific alert for unusual behavior
                alert_service.trigger_alert(
                    alert_type="UNUSUAL_BEHAVIOR_ALERT",
                    tourist_id=str(tourist.id),
                    details={
                        "name": tourist.name,
                        "message": ml_anomaly['message'],
                        "detected_by": "ML_ISOLATION_FOREST",
                        "anomaly_score": ml_anomaly.get('details', {}).get('anomaly_score', 0),
                        "detected_features": ml_anomaly.get('details', {}).get('detected_features', []),
                        "current_location": {
                            "latitude": latest_location.latitude,
                            "longitude": latest_location.longitude,
                            "timestamp": latest_location.timestamp.isoformat()
                        }
                    }
                )
                # Log this new type of anomaly to the ledger
                ledger_service.log_anomaly_event_to_ledger(
                    db=db,
                    tourist_id=tourist.id,
                    anomaly_type="BEHAVIORAL_ML",
                    details=ml_anomaly
                )
            
    except Exception as e:
        print(f"❌ Error running checks for tourist {tourist_id}: {e}")
        
        # Log error to ledger
        ledger_service.log_system_event_to_ledger(
            db=db,
            event_type="ANOMALY_CHECK_ERROR",
            details={
                "tourist_id": str(tourist_id),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


async def run_anomaly_checks_periodically() -> None:
    """
    Background task that runs anomaly checks periodically for all active tourists.
    
    This function runs in an infinite loop, checking all tourists every minute.
    """
    print("🚀 Starting anomaly detection background task")
    
    while True:
        try:
            # Get database session
            db = next(get_db())
            
            try:
                # Get all active tourists (those whose trip hasn't ended)
                current_time = datetime.utcnow()
                active_tourists = db.query(models.Tourist).filter(
                    models.Tourist.trip_end_date > current_time
                ).all()
                
                print(f"🔍 Running anomaly checks for {len(active_tourists)} active tourists")
                
                # Run checks for each active tourist
                for tourist in active_tourists:
                    run_single_tourist_check(db, tourist.id)
                
                print(f"✅ Completed anomaly checks for {len(active_tourists)} tourists")
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error in anomaly detection background task: {e}")
        
        # Wait before next check cycle
        await asyncio.sleep(BACKGROUND_TASK_INTERVAL_SECONDS)


def get_anomaly_detection_status() -> dict:
    """
    Get current status of the anomaly detection system.
    
    Returns:
        Dictionary with system status information
    """
    return {
        "service": "Anomaly Detection Engine",
        "status": "running",
        "configuration": {
            "inactivity_threshold_minutes": INACTIVITY_THRESHOLD_MINUTES,
            "route_deviation_threshold_meters": ROUTE_DEVIATION_THRESHOLD_METERS,
            "check_interval_seconds": BACKGROUND_TASK_INTERVAL_SECONDS
        },
        "features": [
            "Inactivity Detection",
            "Route Deviation Detection", 
            "High-Risk Zone Geo-fencing",
            "Behavioral ML Anomaly Detection",
            "Background Monitoring",
            "Alert Integration",
            "Ledger Integration"
        ]
    }
