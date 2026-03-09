"""
Centralized alert pipeline service.

All alert producers (panic, route deviation, high-risk zone, anomaly detection)
should route through this module so payloads and broadcast behavior stay consistent.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
import logging

from ..api.v1.dashboard_router import manager

logger = logging.getLogger(__name__)


async def trigger_alert(
    alert_type: str,
    tourist_id: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generic alert entrypoint for compatibility with existing callers.

    This keeps the historical `trigger_alert` function available while ensuring
    all messages now go through the unified alert object + websocket format.
    """
    location = details.get("location") or details.get("current_location") or details.get("last_location") or {}
    latitude = location.get("latitude") if isinstance(location, dict) else None
    longitude = location.get("longitude") if isinstance(location, dict) else None
    timestamp = details.get("timestamp")

    if isinstance(timestamp, str):
        try:
            parsed_ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            parsed_ts = datetime.utcnow()
    elif isinstance(timestamp, datetime):
        parsed_ts = timestamp
    else:
        parsed_ts = datetime.utcnow()

    alert = await create_and_broadcast_alert(
        user_id=tourist_id,
        alert_type=alert_type,
        latitude=latitude,
        longitude=longitude,
        risk_score=float(details.get("risk_score", 0.0) or 0.0),
        status=str(details.get("status", "OPEN")),
        timestamp=parsed_ts,
        extra_payload=details,
    )
    return alert


async def create_and_broadcast_alert(
    user_id: str,
    alert_type: str,
    latitude: Optional[float],
    longitude: Optional[float],
    risk_score: float,
    status: str = "OPEN",
    timestamp: Optional[datetime] = None,
    extra_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized alert object and broadcast to dashboard and user channels.

    Returns the created alert payload.
    """
    ts = timestamp or datetime.utcnow()

    alert_obj = {
        "id": str(uuid.uuid4()),
        "user_id": str(user_id),
        "timestamp": ts.isoformat(),
        "latitude": latitude,
        "longitude": longitude,
        "alert_type": alert_type,
        "risk_score": float(max(0.0, min(1.0, risk_score))),
        "status": status,
    }

    event_payload = {
        "event": "alert_triggered",
        "alert_type": alert_type,
        "location": {
            "lat": latitude,
            "lon": longitude,
        },
        "risk_score": alert_obj["risk_score"],
        "alert": alert_obj,
    }

    if extra_payload:
        event_payload["details"] = extra_payload

    # Backward-compatible envelope for existing consumers.
    legacy_payload = {
        "event_type": alert_type,
        "payload": {
            "tourist_id": str(user_id),
            **(extra_payload or {}),
            "alert": alert_obj,
        },
    }

    try:
        await manager.broadcast(event_payload)
        await manager.broadcast_user(str(user_id), event_payload)
        await manager.broadcast(legacy_payload)
        await manager.broadcast_user(str(user_id), legacy_payload)
        logger.info("Alert broadcasted: %s for user %s", alert_type, user_id)
    except Exception as exc:
        logger.exception("Alert broadcast failed for user %s: %s", user_id, exc)

    return alert_obj


async def trigger_panic_alert(
    tourist_id: str,
    name: str,
    location: Dict[str, Any],
    timestamp: Any,
) -> Dict[str, Any]:
    """Trigger panic alert."""
    ts = timestamp if isinstance(timestamp, datetime) else datetime.utcnow()
    if isinstance(timestamp, str):
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            ts = datetime.utcnow()

    return await trigger_alert(
        alert_type="PANIC_ALERT",
        tourist_id=tourist_id,
        details={
            "name": name,
            "location": location,
            "timestamp": ts.isoformat(),
            "priority": "HIGH",
            "requires_immediate_response": True,
        },
    )


async def trigger_inactivity_alert(
    tourist_id: str,
    name: str,
    last_location: Dict[str, Any],
    last_seen: str,
    inactivity_duration: str,
) -> Dict[str, Any]:
    """Trigger inactivity alert."""
    return await trigger_alert(
        alert_type="INACTIVITY_ALERT",
        tourist_id=tourist_id,
        details={
            "name": name,
            "last_location": last_location,
            "last_seen": last_seen,
            "inactivity_duration": inactivity_duration,
            "priority": "MEDIUM",
            "detected_by": "AI_MONITORING_SYSTEM",
        },
    )


async def trigger_location_alert(
    tourist_id: str,
    name: str,
    current_location: Dict[str, Any],
    alert_reason: str,
    timestamp: str,
    risk_score: float = 0.0,
) -> Dict[str, Any]:
    """Trigger location-based alert."""
    return await trigger_alert(
        alert_type="LOCATION_ALERT",
        tourist_id=tourist_id,
        details={
            "name": name,
            "current_location": current_location,
            "location": current_location,
            "alert_reason": alert_reason,
            "timestamp": timestamp,
            "risk_score": risk_score,
            "priority": "MEDIUM",
        },
    )


async def trigger_alert_resolved(
    tourist_id: str,
    name: str,
    resolved_by: str,
    resolution_notes: str,
) -> Dict[str, Any]:
    """Trigger resolution event for an alert."""
    return await trigger_alert(
        alert_type="ALERT_RESOLVED",
        tourist_id=tourist_id,
        details={
            "name": name,
            "resolved_by": resolved_by,
            "resolution_notes": resolution_notes,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "INFO",
            "incident_closed": True,
            "status": "RESOLVED",
        },
    )


__all__ = [
    "trigger_alert",
    "create_and_broadcast_alert",
    "trigger_panic_alert",
    "trigger_inactivity_alert",
    "trigger_location_alert",
    "trigger_alert_resolved",
]
