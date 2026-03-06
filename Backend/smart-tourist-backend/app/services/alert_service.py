"""
🚨 Centralized Alert Broadcasting Service

This service provides a unified interface for triggering real-time alerts
throughout the Smart Tourist Safety Monitoring system. It abstracts the
complexity of alert formatting and WebSocket broadcasting, making it easy
for other developers to send notifications.

Usage Examples:
    # Panic button alert (Developer 2)
    await trigger_alert(
        alert_type="PANIC_ALERT",
        tourist_id="123e4567-e89b-12d3-a456-426614174000",
        details={
            "name": "Alice Johnson",
            "location": {"latitude": 12.9716, "longitude": 77.5946},
            "timestamp": "2025-09-15T14:30:00Z"
        }
    )
    
    # AI anomaly detection alert (Developer 3)
    await trigger_alert(
        alert_type="INACTIVITY_ALERT",
        tourist_id="987fcdeb-51d4-43e8-9f12-345678901234",
        details={
            "name": "Bob Smith",
            "last_seen": "2025-09-15T10:00:00Z",
            "location": {"latitude": 12.9700, "longitude": 77.5900},
            "inactivity_duration": "4 hours"
        }
    )
"""

import json
from datetime import datetime
from typing import Dict, Any

# Import the manager instance from the dashboard router
from ..api.v1.dashboard_router import manager


async def trigger_alert(alert_type: str, tourist_id: str, details: Dict[str, Any]) -> None:
    """
    Trigger a real-time alert broadcast to all connected dashboard clients
    
    This function provides a standardized way to broadcast alerts throughout
    the system. It handles payload formatting and WebSocket broadcasting,
    making it easy for other services to send notifications without dealing
    with WebSocket implementation details.
    
    Args:
        alert_type (str): The type of alert being triggered
                         Examples: "PANIC_ALERT", "INACTIVITY_ALERT", "LOCATION_ALERT"
        tourist_id (str): UUID of the tourist involved in the alert
        details (dict): Additional alert-specific data including:
                       - name: Tourist's name
                       - location: GPS coordinates and timestamp
                       - Any other relevant context data
    
    Returns:
        None: This function broadcasts the alert and returns nothing
        
    Raises:
        Exception: If broadcasting fails, exceptions are handled gracefully
                  to prevent disrupting the calling service
    
    Example:
        >>> await trigger_alert(
        ...     alert_type="PANIC_ALERT",
        ...     tourist_id="uuid-here",
        ...     details={
        ...         "name": "Alice Johnson",
        ...         "location": {"latitude": 12.9716, "longitude": 77.5946},
        ...         "timestamp": "2025-09-15T14:30:00Z"
        ...     }
        ... )
    """
    try:
        # Construct standardized alert payload for frontend consumption
        alert_payload = {
            "event_type": alert_type,  # Standard event type for frontend routing
            "payload": {
                "tourist_id": tourist_id,
                **details  # Unpack all additional details into the payload
            }
        }
        
        # Broadcast the alert to all connected dashboard clients
        await manager.broadcast(alert_payload)
        
        # Optional: Log successful alert broadcast for monitoring
        print(f"✅ Alert broadcasted: {alert_type} for tourist {tourist_id}")
        
    except Exception as e:
        # Handle broadcasting errors gracefully to avoid disrupting caller
        print(f"❌ Alert broadcast failed: {alert_type} for tourist {tourist_id}. Error: {str(e)}")
        # In production, you would use proper logging here instead of print


async def trigger_panic_alert(tourist_id: str, name: str, location: Dict[str, Any], timestamp: str) -> None:
    """
    Convenience function for triggering panic button alerts
    
    This is a specialized wrapper around trigger_alert specifically for panic
    button events. It provides a more convenient interface for Developer 2
    who is implementing the panic button functionality.
    
    Args:
        tourist_id (str): UUID of the tourist in distress
        name (str): Tourist's full name
        location (dict): GPS coordinates with latitude and longitude
        timestamp (str): ISO timestamp of when panic button was pressed
    
    Example:
        >>> await trigger_panic_alert(
        ...     tourist_id="123e4567-e89b-12d3-a456-426614174000",
        ...     name="Alice Johnson",
        ...     location={"latitude": 12.9716, "longitude": 77.5946},
        ...     timestamp="2025-09-15T14:30:00Z"
        ... )
    """
    await trigger_alert(
        alert_type="PANIC_ALERT",
        tourist_id=tourist_id,
        details={
            "name": name,
            "location": location,
            "timestamp": timestamp,
            "priority": "HIGH",  # Panic alerts are always high priority
            "requires_immediate_response": True
        }
    )


async def trigger_inactivity_alert(tourist_id: str, name: str, last_location: Dict[str, Any], 
                                 last_seen: str, inactivity_duration: str) -> None:
    """
    Convenience function for triggering AI-detected inactivity alerts
    
    This is a specialized wrapper around trigger_alert specifically for
    AI anomaly detection events. It provides a convenient interface for
    Developer 3 who is implementing the AI monitoring system.
    
    Args:
        tourist_id (str): UUID of the inactive tourist
        name (str): Tourist's full name
        last_location (dict): Last known GPS coordinates
        last_seen (str): ISO timestamp of last activity
        inactivity_duration (str): Human-readable duration of inactivity
    
    Example:
        >>> await trigger_inactivity_alert(
        ...     tourist_id="987fcdeb-51d4-43e8-9f12-345678901234",
        ...     name="Bob Smith",
        ...     last_location={"latitude": 12.9700, "longitude": 77.5900},
        ...     last_seen="2025-09-15T10:00:00Z",
        ...     inactivity_duration="4 hours"
        ... )
    """
    await trigger_alert(
        alert_type="INACTIVITY_ALERT",
        tourist_id=tourist_id,
        details={
            "name": name,
            "last_location": last_location,
            "last_seen": last_seen,
            "inactivity_duration": inactivity_duration,
            "priority": "MEDIUM",  # Inactivity alerts are medium priority
            "detected_by": "AI_MONITORING_SYSTEM"
        }
    )


async def trigger_location_alert(tourist_id: str, name: str, current_location: Dict[str, Any],
                               alert_reason: str, timestamp: str) -> None:
    """
    Convenience function for triggering location-based alerts
    
    This function can be used for various location-based scenarios such as
    entering restricted areas, moving outside safe zones, or being in
    dangerous locations.
    
    Args:
        tourist_id (str): UUID of the tourist
        name (str): Tourist's full name
        current_location (dict): Current GPS coordinates
        alert_reason (str): Reason for the location alert
        timestamp (str): ISO timestamp of the alert
    
    Example:
        >>> await trigger_location_alert(
        ...     tourist_id="456e7890-e89b-12d3-a456-426614174000",
        ...     name="Charlie Wilson",
        ...     current_location={"latitude": 12.9800, "longitude": 77.6000},
        ...     alert_reason="Entered restricted area",
        ...     timestamp="2025-09-15T16:00:00Z"
        ... )
    """
    await trigger_alert(
        alert_type="LOCATION_ALERT",
        tourist_id=tourist_id,
        details={
            "name": name,
            "current_location": current_location,
            "alert_reason": alert_reason,
            "timestamp": timestamp,
            "priority": "MEDIUM"
        }
    )


async def trigger_alert_resolved(tourist_id: str, name: str, resolved_by: str, resolution_notes: str) -> None:
    """
    Convenience function for triggering alert resolution notifications
    
    This function is used when an incident is resolved and authorities need to be
    notified that an alert can be cleared from the dashboard. It completes the
    incident lifecycle by providing closure information for audit trails.
    
    Args:
        tourist_id (str): UUID of the tourist whose alert is being resolved
        name (str): Tourist's full name
        resolved_by (str): Name/ID of the person who resolved the incident
        resolution_notes (str): Details about how the incident was resolved
    
    Example:
        >>> await trigger_alert_resolved(
        ...     tourist_id="123e4567-e89b-12d3-a456-426614174000",
        ...     name="Alice Johnson",
        ...     resolved_by="Dispatcher Sharma",
        ...     resolution_notes="Contacted tourist, confirmed safe. Was in area with poor signal."
        ... )
    """
    await trigger_alert(
        alert_type="ALERT_RESOLVED",
        tourist_id=tourist_id,
        details={
            "name": name,
            "resolved_by": resolved_by,  # e.g., "Dispatcher Sharma"
            "resolution_notes": resolution_notes,  # e.g., "Contacted tourist, confirmed safe."
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "INFO",  # Resolution notifications are informational
            "incident_closed": True
        }
    )


# Export the main function for other developers to use
__all__ = ["trigger_alert", "trigger_panic_alert", "trigger_inactivity_alert", "trigger_location_alert", "trigger_alert_resolved"]
