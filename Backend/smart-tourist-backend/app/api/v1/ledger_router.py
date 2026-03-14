"""
Ledger API Router - HTTP Endpoints for Event Logging

This module provides HTTP endpoints for the Auth & Location services
to append events to the tamper-evident ledger.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

from ...db.session import get_db
from ...services import ledger_service
from ...db import models

router = APIRouter(prefix="/internal/ledger", tags=["Internal Ledger API"])


# Request/Response Schemas
class EventRequest(BaseModel):
    """Request schema for logging events to the ledger"""
    tourist_id: str = Field(..., description="UUID of the tourist")
    event_type: str = Field(..., description="Type of event (PANIC, REGISTER, AI_ANOMALY, etc.)")
    event_data: Dict[str, Any] = Field(..., description="Event payload data")
    
    class Config:
        schema_extra = {
            "example": {
                "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "PANIC",
                "event_data": {
                    "location": {"latitude": 12.9716, "longitude": 77.5946},
                    "timestamp": "2025-09-15T14:30:00Z",
                    "device_id": "tourist_device_001"
                }
            }
        }


class EventResponse(BaseModel):
    """Response schema for logged events"""
    success: bool
    block_id: int = Field(..., description="Database ID of the created block")
    proof_hash: str = Field(..., description="Tamper-evident hash for immutable proof")
    tourist_id: str
    event_type: str
    timestamp: datetime
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "block_id": 1025,
                "proof_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "PANIC",
                "timestamp": "2025-09-15T14:30:00.123456",
                "message": "Event successfully logged to tamper-evident ledger"
            }
        }


# Internal API Key validation (simplified for internal services)
def validate_internal_api_key(api_key: Optional[str] = None) -> bool:
    """
    Validate internal API key for service-to-service communication
    In production, this would check against LEDGER_INTERNAL_API_KEY env var
    """
    # For now, accept any non-empty key or no key for internal testing
    # In production: return api_key == os.getenv("LEDGER_INTERNAL_API_KEY")
    return True


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def log_event_to_ledger(
    request: EventRequest,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> EventResponse:
    """
    **Internal API** - Log an event to the tamper-evident ledger
    
    This endpoint is used by Auth & Location services to append events
    to the blockchain-inspired ledger for immutable audit trails.
    
    **Authentication**: Internal API key required in production
    **Network**: Internal service communication only
    
    Args:
        request: Event data to be logged
        db: Database session dependency
        api_key: Internal API key (passed via header or query param)
    
    Returns:
        EventResponse with immutable proof hash
        
    Raises:
        HTTPException: 401 if API key invalid, 500 if logging fails
    """
    try:
        # Validate API key for internal service access
        if not validate_internal_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing internal API key"
            )
        
        # Create standardized event data for the ledger
        standardized_event_data = {
            "event": request.event_type,
            "details": request.event_data,
            "logged_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Log the event to the tamper-evident ledger
        ledger_block = ledger_service.add_new_block(
            db=db,
            tourist_id=request.tourist_id,
            event_data=standardized_event_data
        )
        
        # Return the response with immutable proof
        return EventResponse(
            success=True,
            block_id=ledger_block.id,
            proof_hash=ledger_block.current_hash,  # This is the immutable proof
            tourist_id=ledger_block.tourist_id,
            event_type=request.event_type,
            timestamp=ledger_block.timestamp,
            message="Event successfully logged to tamper-evident ledger"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like auth failures)
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log event to ledger: {str(e)}"
        )


@router.post("/events/panic", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def log_panic_event(
    tourist_id: str,
    location_data: Dict[str, Any],
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> EventResponse:
    """
    **Convenience Endpoint** - Log a panic event to the ledger
    
    This is a specialized endpoint for panic events that uses the
    existing log_panic_event_to_ledger function.
    
    Args:
        tourist_id: UUID of the tourist
        location_data: Location information dictionary
        db: Database session dependency
        api_key: Internal API key
    
    Returns:
        EventResponse with immutable proof hash
    """
    try:
        # Validate API key
        if not validate_internal_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing internal API key"
            )
        
        # Use the existing panic logging function
        ledger_service.log_panic_event_to_ledger(
            db=db,
            tourist_id=tourist_id,
            location_data=location_data
        )
        
        # Get the latest block (which should be the one we just created)
        latest_block = ledger_service.get_latest_block_hash(db)
        latest_block_obj = db.query(models.IDLedger).order_by(models.IDLedger.id.desc()).first()
        
        return EventResponse(
            success=True,
            block_id=latest_block_obj.id,
            proof_hash=latest_block_obj.current_hash,
            tourist_id=tourist_id,
            event_type="PANIC",
            timestamp=latest_block_obj.timestamp,
            message="Panic event successfully logged to tamper-evident ledger"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log panic event: {str(e)}"
        )


@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_ledger_integrity(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    **Internal API** - Verify the integrity of the tamper-evident ledger
    
    This endpoint allows internal services to verify that the ledger
    chain has not been tampered with.
    
    Returns:
        Dictionary with verification status and details
    """
    try:
        # Validate API key
        if not validate_internal_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing internal API key"
            )
        
        # Verify the ledger chain
        is_valid = ledger_service.verify_chain(db)
        
        return {
            "success": True,
            "chain_valid": is_valid,
            "message": "Ledger integrity verified" if is_valid else "CRITICAL: Ledger tampering detected",
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify ledger: {str(e)}"
        )
