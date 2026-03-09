"""
Tourist Tracking and Alert API Router

This module provides API endpoints for tourist location tracking and panic alerts.
It serves as the core data ingestion layer for the mobile apps, handling the
continuous stream of location data and the critical panic button functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging

# Database dependencies
from ...db.session import get_db

# Import CRUD operations
from ...crud import crud_tourist

# Import services for alert broadcasting and ledger logging
from ...services import alert_service, ledger_service, accessibility_service
from ...services.route_monitor_service import route_monitor_service
from ...ml.risk_model import predict_risk

# Import schemas
from ...schemas import tourist as schemas

# Create router instance
router = APIRouter(prefix="/tourists", tags=["Tourist Tracking & Alerts"])
logger = logging.getLogger(__name__)


@router.post("/{tourist_id}/location", status_code=status.HTTP_201_CREATED)
async def log_tourist_location(
    tourist_id: str,
    location_data: schemas.LocationCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Log tourist's current location for tracking purposes
    
    This endpoint receives GPS coordinates from the mobile app and stores
    them in the location_logs table for tracking and monitoring purposes.
    It provides the "heartbeat" of the system by continuously updating
    tourist locations.
    
    **Integration Points:**
    - Creates location log via CRUD layer
    - Stores GPS coordinates with timestamp
    - Used for regular location tracking
    
    Args:
        tourist_id: UUID string of the tourist
        location_data: GPS coordinates from mobile app
        db: Database session dependency
        
    Returns:
        Dict: Success confirmation message
        
    Raises:
        HTTPException: 500 if location logging fails
        
    Example Request:
        ```json
        {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        ```
        
    Example Response:
        ```json
        {
            "status": "success",
            "message": "Location logged."
        }
        ```
    """
    try:
        # Log the location using CRUD layer
        location_log = crud_tourist.create_location_log(
            db=db,
            tourist_id=tourist_id,
            location=location_data
        )

        tourist = crud_tourist.get_tourist(db, tourist_id)
        tourist_name = tourist.name if tourist else f"Tourist-{tourist_id[:8]}"

        prediction = predict_risk(
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            timestamp=location_log.timestamp,
            db=db
        )

        route_deviation = route_monitor_service.check_route_deviation(
            tourist_id=tourist_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            threshold_meters=100.0,
        )

        if route_deviation:
            await alert_service.create_and_broadcast_alert(
                user_id=tourist_id,
                alert_type="ROUTE_DEVIATION",
                latitude=location_data.latitude,
                longitude=location_data.longitude,
                risk_score=float(prediction["risk_score"]),
                extra_payload={
                    "name": tourist_name,
                    "deviation_meters": route_deviation["deviation_meters"],
                    "threshold_meters": route_deviation["threshold_meters"],
                    "timestamp": location_log.timestamp.isoformat(),
                },
            )

        if float(prediction["risk_score"]) > 0.75:
            await alert_service.create_and_broadcast_alert(
                user_id=tourist_id,
                alert_type="HIGH_RISK_AREA",
                latitude=location_data.latitude,
                longitude=location_data.longitude,
                risk_score=float(prediction["risk_score"]),
                extra_payload={
                    "name": tourist_name,
                    "danger_level": prediction["danger_level"],
                    "timestamp": location_log.timestamp.isoformat(),
                },
            )
        
        # Return success confirmation
        return {
            "status": "success",
            "message": "Location logged.",
            "risk_score": float(prediction["risk_score"]),
            "danger_level": prediction["danger_level"],
        }
        
    except Exception as e:
        # Handle any errors during location logging
        db.rollback()  # Rollback any partial database changes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log location: {str(e)}"
        )


@router.post("/{tourist_id}/route", status_code=status.HTTP_200_OK)
async def set_planned_route(
    tourist_id: str,
    route: schemas.PlannedRouteRequest,
) -> Dict[str, Any]:
    """
    Register a tourist's planned route for route deviation monitoring.
    """
    try:
        coordinates = [(point.latitude, point.longitude) for point in route.coordinates]
        route_monitor_service.set_planned_route(tourist_id=tourist_id, coordinates=coordinates)
        return {
            "status": "success",
            "message": "Planned route registered.",
            "points": len(coordinates),
            "updated_at": datetime.utcnow().isoformat(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to register planned route for tourist %s", tourist_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register planned route: {exc}"
        )


@router.post("/{tourist_id}/panic")
async def trigger_panic_button(
    tourist_id: str,
    location_data: schemas.LocationCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger panic alert with immediate broadcasting and ledger logging
    
    This is the MOST CRITICAL endpoint in the system. When a tourist presses
    the panic button, this endpoint immediately:
    1. Logs the panic location
    2. Verifies tourist exists
    3. Broadcasts real-time alert to dashboard
    4. Creates tamper-evident ledger entry
    
    **CRITICAL INTEGRATION POINTS:**
    - Real-time WebSocket broadcasting via alert_service
    - Tamper-evident logging via ledger_service
    - Immediate location capture for emergency response
    
    Args:
        tourist_id: UUID string of the tourist in distress
        location_data: GPS coordinates from panic location
        db: Database session dependency
        
    Returns:
        Dict: Success confirmation with alert details
        
    Raises:
        HTTPException: 404 if tourist not found, 500 if panic processing fails
        
    Example Request:
        ```json
        {
            "latitude": 40.7589,
            "longitude": -73.9851
        }
        ```
        
    Example Response:
        ```json
        {
            "status": "success",
            "message": "Panic alert triggered and logged."
        }
        ```
    """
    try:
        # Step 1: **Log the location** - Capture panic location immediately
        location_log = crud_tourist.create_location_log(
            db=db,
            tourist_id=tourist_id,
            location=location_data
        )
        
        # Step 2: **Verify tourist exists** - Get tourist details for alert
        tourist = crud_tourist.get_tourist(db, tourist_id)
        if tourist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Step 3: **CRITICAL INTEGRATION 1** - Real-time alert broadcasting
        # Prepare location dictionary for alert service
        location_dict = {
            "latitude": location_data.latitude,
            "longitude": location_data.longitude
        }
        
        # Broadcast panic alert to dashboard via WebSocket
        await alert_service.trigger_panic_alert(
            tourist_id=tourist_id,
            name=tourist.name,
            location=location_dict,
            timestamp=location_log.timestamp
        )
        
        # Step 4: **CRITICAL INTEGRATION 2** - Tamper-evident ledger logging
        # Log panic event to immutable ledger for evidence chain
        ledger_service.log_panic_event_to_ledger(
            db=db,
            tourist_id=tourist_id,
            location_data=location_dict
        )
        
        # Step 5: Return success confirmation
        return {
            "status": "success",
            "message": "Panic alert triggered and logged."
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like tourist not found)
        raise
    except Exception as e:
        # Handle any other errors during panic processing
        db.rollback()  # Rollback any partial database changes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process panic alert: {str(e)}"
        )


@router.post("/{tourist_id}/text-alert")
async def handle_text_alert(
    tourist_id: str,
    request: schemas.TextAlertRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process multilingual text alerts for automatic distress detection
    
    This endpoint provides accessibility by analyzing text messages for distress
    keywords in multiple Indian languages. When distress is detected, it automatically
    triggers the full panic alert workflow, providing an alternative to the panic button
    for tourists who may have difficulty accessing it.
    
    **Supported Languages:**
    - English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada
    - Automatic detection of distress keywords like "मदद", "help", "সাহায্য", etc.
    - Advanced pattern matching for emotional distress indicators
    
    **Critical Integration:**
    - Automatic panic alert triggering for detected distress
    - Real-time dashboard broadcasting
    - Tamper-evident ledger logging
    - Enhanced location data with detection context
    
    Args:
        tourist_id: UUID string of the tourist sending the text alert
        request: TextAlertRequest containing message and location data
        db: Database session dependency
        
    Returns:
        Dict: Response indicating whether distress was detected and processed
        
    Raises:
        HTTPException: 500 if text processing fails
        
    Example Requests:
        ```json
        {
            "message": "मदद करो! मैं खो गया हूं",
            "latitude": 40.7589,
            "longitude": -73.9851
        }
        ```
        
        ```json
        {
            "message": "help me please I'm lost",
            "latitude": 40.7589,
            "longitude": -73.9851
        }
        ```
        
    Example Responses:
        Distress Detected:
        ```json
        {
            "status": "alert_triggered",
            "message": "Distress detected in message. Emergency alert has been triggered.",
            "detected_language": "hindi",
            "detected_keyword": "मदद",
            "emergency_response": "activated"
        }
        ```
        
        No Distress:
        ```json
        {
            "status": "message_received",
            "message": "Message received. No distress detected.",
            "emergency_response": "none"
        }
        ```
    """
    try:
        # Prepare location data for processing
        location_data = {
            "latitude": request.latitude,
            "longitude": request.longitude
        }
        
        # Process the text message through accessibility service
        distress_detected = await accessibility_service.process_text_alert(
            db=db,
            tourist_id=tourist_id,
            text_message=request.message,
            location_data=location_data
        )
        
        # Return different responses based on distress detection
        if distress_detected:
            # Distress was detected and emergency alert was triggered
            # Get additional analysis for the response
            analysis = accessibility_service.analyze_message_content(request.message)
            
            return {
                "status": "alert_triggered",
                "message": "Distress detected in message. Emergency alert has been triggered.",
                "detected_language": analysis.get("detected_languages", ["unknown"])[0] if analysis.get("detected_languages") else "unknown",
                "detected_keyword": analysis.get("detected_keywords", ["unknown"])[0] if analysis.get("detected_keywords") else "unknown",
                "confidence_level": analysis.get("confidence", "medium"),
                "emergency_response": "activated",
                "alert_timestamp": "triggered",
                "location_logged": True,
                "dashboard_notified": True,
                "ledger_recorded": True
            }
        else:
            # No distress detected - message received but no emergency response needed
            return {
                "status": "message_received", 
                "message": "Message received. No distress detected.",
                "emergency_response": "none",
                "analysis_performed": True,
                "supported_languages": accessibility_service.get_supported_languages()
            }
            
    except Exception as e:
        # Handle any errors during text alert processing
        db.rollback()  # Rollback any partial database changes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process text alert: {str(e)}"
        )
