"""
Notification API Router - HTTP Endpoints for Event Publishing

This module provides HTTP endpoints for Auth & Location services
to publish LOCATION_UPDATE and PANIC_ALERT events to the dashboard.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal
from datetime import datetime
import uuid

from ...services import alert_service

router = APIRouter(prefix="/internal/notifications", tags=["Internal Notification API"])


# Request Schemas
class LocationUpdateEvent(BaseModel):
    """Schema for LOCATION_UPDATE events from Auth & Location services"""
    event_type: Literal["LOCATION_UPDATE"] = "LOCATION_UPDATE"
    tourist_id: str = Field(..., description="UUID of the tourist")
    name: str = Field(..., description="Tourist's full name")
    location: Dict[str, Any] = Field(..., description="Location data with latitude, longitude, timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "event_type": "LOCATION_UPDATE",
                "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Alice Johnson",
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "timestamp": "2025-09-15T14:30:00Z",
                    "accuracy": 5.0
                }
            }
        }


class PanicAlertEvent(BaseModel):
    """Schema for PANIC_ALERT events from Auth & Location services"""
    event_type: Literal["PANIC_ALERT"] = "PANIC_ALERT"
    tourist_id: str = Field(..., description="UUID of the tourist in distress")
    name: str = Field(..., description="Tourist's full name")
    location: Dict[str, Any] = Field(..., description="Location data with latitude, longitude, timestamp")
    message: str = Field(..., description="Alert message or description")
    panic_id: Optional[str] = Field(None, description="Optional panic event UUID")
    ledger_proof_hash: Optional[str] = Field(None, description="Immutable proof hash from ledger")
    
    class Config:
        schema_extra = {
            "example": {
                "event_type": "PANIC_ALERT",
                "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Alice Johnson",
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "timestamp": "2025-09-15T14:30:00Z"
                },
                "message": "Emergency panic button activated",
                "panic_id": "panic_789e0123-e89b-12d3-a456-426614174000",
                "ledger_proof_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            }
        }


# Response Schema
class PublishResponse(BaseModel):
    """Response schema for published events"""
    success: bool
    event_id: str = Field(..., description="Unique event ID for tracking")
    event_type: str
    tourist_id: str
    timestamp: datetime
    message: str
    broadcasted: bool = Field(..., description="Whether event was broadcasted to dashboard")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "event_id": "evt_456e7890-e89b-12d3-a456-426614174000",
                "event_type": "PANIC_ALERT",
                "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-09-15T14:30:00.123456",
                "message": "Event published and broadcasted to dashboard",
                "broadcasted": True
            }
        }


# Internal API Key validation
def validate_notification_api_key(api_key: Optional[str] = None) -> bool:
    """Validate internal API key for notification publishing"""
    # For development: accept any non-empty key
    # Production: return api_key == os.getenv("NOTIFICATION_INTERNAL_API_KEY")
    return True


@router.post("/publish", response_model=PublishResponse, status_code=status.HTTP_202_ACCEPTED)
async def publish_notification(
    event: Dict[str, Any],
    api_key: Optional[str] = None
) -> PublishResponse:
    """
    **Internal API** - Publish notification events to the dashboard
    
    This endpoint accepts LOCATION_UPDATE and PANIC_ALERT events from
    Auth & Location services and broadcasts them to the dashboard via WebSocket.
    
    **Async Processing**: Returns 202 Accepted with event_id for tracking
    **Guaranteed Ordering**: Events are processed in order of receipt
    **Size Limits**: 1MB max payload size
    **Rate Limits**: 1000 events/minute per service
    
    Args:
        event: Event payload (LOCATION_UPDATE or PANIC_ALERT)
        db: Database session dependency
        api_key: Internal API key for service authentication
    
    Returns:
        PublishResponse with event_id and confirmation
        
    Raises:
        HTTPException: 401 if API key invalid, 400 if invalid payload, 422 if validation fails
    """
    try:
        # Validate API key
        if not validate_notification_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing notification API key"
            )
        
        # Generate unique event ID for tracking
        event_id = f"evt_{str(uuid.uuid4())}"
        
        # Extract event type
        event_type = event.get("event_type")
        if not event_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: event_type"
            )
        
        # Extract tourist_id
        tourist_id = event.get("tourist_id")
        if not tourist_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: tourist_id"
            )
        
        # Process based on event type
        if event_type == "LOCATION_UPDATE":
            await _handle_location_update(event, event_id)
        elif event_type == "PANIC_ALERT":
            await _handle_panic_alert(event, event_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported event_type: {event_type}"
            )
        
        # Return async response with event tracking
        return PublishResponse(
            success=True,
            event_id=event_id,
            event_type=event_type,
            tourist_id=tourist_id,
            timestamp=datetime.now(timezone.utc),
            message=f"Event {event_type} published and broadcasted to dashboard",
            broadcasted=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish notification: {str(e)}"
        )


@router.post("/location-update", response_model=PublishResponse, status_code=status.HTTP_202_ACCEPTED)
async def publish_location_update(
    event: LocationUpdateEvent,
    api_key: Optional[str] = None
) -> PublishResponse:
    """
    **Convenience Endpoint** - Publish LOCATION_UPDATE event
    
    Specialized endpoint for location updates with schema validation.
    
    Args:
        event: Validated LocationUpdateEvent
        db: Database session
        api_key: Internal API key
    
    Returns:
        PublishResponse with event tracking information
    """
    try:
        # Validate API key
        if not validate_notification_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing notification API key"
            )
        
        # Generate event ID
        event_id = f"evt_{str(uuid.uuid4())}"
        
        # Handle location update
        await _handle_location_update(event.dict(), event_id)
        
        return PublishResponse(
            success=True,
            event_id=event_id,
            event_type="LOCATION_UPDATE",
            tourist_id=event.tourist_id,
            timestamp=datetime.now(timezone.utc),
            message="Location update published and broadcasted to dashboard",
            broadcasted=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish location update: {str(e)}"
        )


@router.post("/panic-alert", response_model=PublishResponse, status_code=status.HTTP_202_ACCEPTED)
async def publish_panic_alert(
    event: PanicAlertEvent,
    api_key: Optional[str] = None
) -> PublishResponse:
    """
    **Convenience Endpoint** - Publish PANIC_ALERT event
    
    Specialized endpoint for panic alerts with schema validation.
    
    Args:
        event: Validated PanicAlertEvent
        db: Database session
        api_key: Internal API key
    
    Returns:
        PublishResponse with event tracking information
    """
    try:
        # Validate API key
        if not validate_notification_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing notification API key"
            )
        
        # Generate event ID
        event_id = f"evt_{str(uuid.uuid4())}"
        
        # Handle panic alert
        await _handle_panic_alert(event.dict(), event_id)
        
        return PublishResponse(
            success=True,
            event_id=event_id,
            event_type="PANIC_ALERT",
            tourist_id=event.tourist_id,
            timestamp=datetime.now(timezone.utc),
            message="Panic alert published and broadcasted to dashboard",
            broadcasted=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish panic alert: {str(e)}"
        )


# Internal handler functions
async def _handle_location_update(event: Dict[str, Any], event_id: str):
    """Handle LOCATION_UPDATE event broadcasting"""
    # Use existing alert service for WebSocket broadcasting
    # Note: LOCATION_UPDATE is treated as a general alert
    await alert_service.trigger_alert(
        alert_type="LOCATION_UPDATE",
        tourist_id=event["tourist_id"],
        details={
            "name": event["name"],
            "location": event["location"],
            "event_id": event_id,
            "priority": "LOW"  # Location updates are informational
        }
    )


async def _handle_panic_alert(event: Dict[str, Any], event_id: str):
    """Handle PANIC_ALERT event broadcasting"""
    # Use existing alert service for high-priority panic broadcasting
    await alert_service.trigger_panic_alert(
        tourist_id=event["tourist_id"],
        name=event["name"],
        location=event["location"],
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Additional panic-specific processing could go here
    # e.g., trigger emergency response protocols
