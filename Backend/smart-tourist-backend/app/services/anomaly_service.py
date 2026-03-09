"""Async anomaly detection engine for periodic backend monitoring."""

import asyncio
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session

from app.crud import crud_tourist
from app.db import models
from app.db.session import get_db
from app.ml.risk_model import predict_risk
from app.services import alert_service, ml_anomaly_service
from app.services.route_monitor_service import route_monitor_service

logger = logging.getLogger(__name__)

INACTIVITY_THRESHOLD_MINUTES = 60
ROUTE_DEVIATION_THRESHOLD_METERS = 100
HIGH_RISK_THRESHOLD = 0.75
BACKGROUND_TASK_INTERVAL_SECONDS = 60


async def check_inactivity(db: Session, tourist: models.Tourist, latest_location: models.LocationLog) -> None:
    """Check inactivity threshold and trigger alert if exceeded."""
    inactivity_delta = datetime.utcnow() - latest_location.timestamp
    if inactivity_delta <= timedelta(minutes=INACTIVITY_THRESHOLD_MINUTES):
        return

    inactivity_minutes = int(inactivity_delta.total_seconds() / 60)
    await alert_service.trigger_inactivity_alert(
        tourist_id=str(tourist.id),
        name=tourist.name,
        last_location={
            "latitude": latest_location.latitude,
            "longitude": latest_location.longitude,
            "timestamp": latest_location.timestamp.isoformat(),
        },
        last_seen=latest_location.timestamp.isoformat(),
        inactivity_duration=f"{inactivity_minutes} minutes",
    )

async def check_route_deviation(db: Session, tourist: models.Tourist, latest_location: models.LocationLog) -> None:
    """Check route deviation from planned route and trigger alert."""
    deviation = route_monitor_service.check_route_deviation(
        tourist_id=str(tourist.id),
        latitude=latest_location.latitude,
        longitude=latest_location.longitude,
        threshold_meters=ROUTE_DEVIATION_THRESHOLD_METERS,
    )
    if not deviation:
        return

    prediction = predict_risk(
        latitude=latest_location.latitude,
        longitude=latest_location.longitude,
        timestamp=latest_location.timestamp,
        db=db,
    )

    await alert_service.create_and_broadcast_alert(
        user_id=str(tourist.id),
        alert_type="ROUTE_DEVIATION",
        latitude=latest_location.latitude,
        longitude=latest_location.longitude,
        risk_score=float(prediction["risk_score"]),
        extra_payload={
            "name": tourist.name,
            "deviation_meters": deviation["deviation_meters"],
            "threshold_meters": deviation["threshold_meters"],
            "timestamp": latest_location.timestamp.isoformat(),
        },
    )

async def check_high_risk_zone(db: Session, tourist: models.Tourist, latest_location: models.LocationLog) -> None:
    """Check ML risk score and trigger high-risk-zone alert."""
    prediction = predict_risk(
        latitude=latest_location.latitude,
        longitude=latest_location.longitude,
        timestamp=latest_location.timestamp,
        db=db,
    )

    risk_score = float(prediction["risk_score"])
    if risk_score <= HIGH_RISK_THRESHOLD:
        return

    await alert_service.create_and_broadcast_alert(
        user_id=str(tourist.id),
        alert_type="HIGH_RISK_AREA",
        latitude=latest_location.latitude,
        longitude=latest_location.longitude,
        risk_score=risk_score,
        extra_payload={
            "name": tourist.name,
            "danger_level": prediction["danger_level"],
            "timestamp": latest_location.timestamp.isoformat(),
        },
    )

async def check_behavioral_ml_anomaly(db: Session, tourist: models.Tourist, latest_location: models.LocationLog) -> None:
    """Check IsolationForest-based behavioral anomaly and alert if detected."""
    anomaly = ml_anomaly_service.detect_behavioral_anomalies(
        db=db,
        tourist_id=str(tourist.id),
        latest_location=latest_location,
    )
    if not anomaly:
        return

    anomaly_score = float(anomaly.get("details", {}).get("anomaly_score", 0.0))
    risk_score = max(0.0, min(1.0, (abs(anomaly_score) + 0.2)))

    await alert_service.create_and_broadcast_alert(
        user_id=str(tourist.id),
        alert_type="ANOMALY_DETECTION",
        latitude=latest_location.latitude,
        longitude=latest_location.longitude,
        risk_score=risk_score,
        extra_payload={
            "name": tourist.name,
            "message": anomaly.get("message", "Behavioral anomaly detected"),
            "detected_by": "ML_ISOLATION_FOREST",
            "anomaly_score": anomaly_score,
            "details": anomaly.get("details", {}),
            "timestamp": latest_location.timestamp.isoformat(),
        },
    )

async def run_single_tourist_check(db: Session, tourist_id: str) -> None:
    """Run anomaly checks for a single tourist."""
    tourist = crud_tourist.get_tourist(db, tourist_id)
    if not tourist:
        return

    latest_location = crud_tourist.get_latest_location_by_tourist_id(db, tourist.id)
    if not latest_location:
        return

    await check_inactivity(db, tourist, latest_location)
    await check_route_deviation(db, tourist, latest_location)
    await check_high_risk_zone(db, tourist, latest_location)
    await check_behavioral_ml_anomaly(db, tourist, latest_location)


async def run_anomaly_checks_periodically() -> None:
    """Background task that periodically checks anomalies for active tourists."""
    logger.info("Starting anomaly detection background task")

    while True:
        db_gen = get_db()
        db = next(db_gen)
        try:
            active_tourists = (
                db.query(models.Tourist)
                .filter(models.Tourist.trip_end_date > datetime.utcnow())
                .all()
            )
            for tourist in active_tourists:
                try:
                    await run_single_tourist_check(db=db, tourist_id=str(tourist.id))
                except Exception:
                    logger.exception("Failed anomaly checks for tourist %s", tourist.id)
        except Exception:
            logger.exception("Error in anomaly detection cycle")
        finally:
            db_gen.close()

        await asyncio.sleep(BACKGROUND_TASK_INTERVAL_SECONDS)


def get_anomaly_detection_status() -> dict:
    """Expose anomaly engine status and configuration."""
    return {
        "service": "Anomaly Detection Engine",
        "status": "running",
        "configuration": {
            "inactivity_threshold_minutes": INACTIVITY_THRESHOLD_MINUTES,
            "route_deviation_threshold_meters": ROUTE_DEVIATION_THRESHOLD_METERS,
            "high_risk_threshold": HIGH_RISK_THRESHOLD,
            "check_interval_seconds": BACKGROUND_TASK_INTERVAL_SECONDS,
        },
        "features": [
            "Inactivity Detection",
            "Route Deviation Detection",
            "High-Risk Zone Detection (ML Risk Score)",
            "Behavioral ML Anomaly Detection",
            "Background Monitoring",
            "Central Alert Pipeline",
        ],
    }
