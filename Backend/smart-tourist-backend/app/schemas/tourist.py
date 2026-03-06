"""
Pydantic schemas for tourist-related API responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class LocationBase(BaseModel):
    """
    Base schema for location data
    
    Represents GPS coordinates with timestamp for tracking tourist locations
    """
    latitude: float
    longitude: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TouristStatus(BaseModel):
    """
    Schema for tourist status in dashboard responses
    
    Represents a tourist's current status including their most recent location
    for dashboard initialization and real-time updates
    """
    tourist_id: UUID
    name: str
    last_known_location: Optional[LocationBase] = None
    status: str = "active"
    
    class Config:
        from_attributes = True


class TouristDetails(BaseModel):
    """
    Schema for detailed tourist information including location history
    
    Used for individual tourist detail views in the dashboard, providing
    comprehensive information including full location tracking history
    """
    tourist_id: UUID
    name: str
    location_history: List[LocationBase]
    
    class Config:
        from_attributes = True


class DashboardAnalytics(BaseModel):
    """
    Schema for dashboard analytics and summary statistics
    
    Provides counts and metrics for the dashboard overview, allowing
    authorities to quickly assess the current state of tourist monitoring
    """
    total: int
    active_with_location: int
    registered_no_location: int
    
    class Config:
        from_attributes = True


# --- NEW SCHEMAS FOR LOCATION TRACKING ---

class LocationCreate(BaseModel):
    """
    Schema for location data submission from mobile apps
    
    Defines the GPS coordinates that tourists' mobile apps will send
    for location tracking and panic button functionality.
    """
    latitude: float
    longitude: float
    
    class Config:
        schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


# --- NEW SCHEMAS FOR ACCESSIBILITY & TEXT ALERTS ---

class TextAlertRequest(BaseModel):
    """
    Schema for multilingual text alert requests
    
    Defines the structure for text-based emergency alerts that can contain
    distress keywords in multiple languages. The accessibility service will
    analyze the message content and automatically trigger panic alerts if
    distress keywords are detected.
    """
    message: str
    latitude: float
    longitude: float
    
    class Config:
        schema_extra = {
            "example": {
                "message": "मदद करो! मैं खो गया हूं",
                "latitude": 40.7589,
                "longitude": -73.9851
            }
        }


# --- NEW SCHEMAS FOR TOURIST REGISTRATION ---

class TouristCreate(BaseModel):
    """
    Schema for tourist registration request body
    
    Defines the required data for registering a new tourist in the system.
    This is the input schema for the POST /register endpoint.
    """
    name: str
    kyc_hash: str
    emergency_contact: Dict[str, Any]
    trip_end_date: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Alice Johnson",
                "kyc_hash": "kyc_abc123def456",
                "emergency_contact": {
                    "name": "John Johnson",
                    "phone": "+1234567890",
                    "email": "emergency@example.com",
                    "relationship": "spouse"
                },
                "trip_end_date": "2025-09-22T18:00:00Z"
            }
        }


class LedgerEntry(BaseModel):
    """
    Schema for ledger entry information in responses
    
    Represents the tamper-evident ledger entry created during registration,
    providing immutable proof of the registration event.
    """
    block_id: int
    hash: str
    timestamp: datetime
    event: str
    
    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    """
    Schema for successful tourist registration response
    
    Returns the newly created tourist information along with the
    tamper-evident ledger entry for audit purposes.
    """
    tourist_id: UUID
    name: str
    ledger_entry: LedgerEntry
    message: str = "Tourist registered successfully"
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Alice Johnson",
                "ledger_entry": {
                    "block_id": 1001,
                    "hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                    "timestamp": "2025-09-15T14:30:00.123456Z",
                    "event": "REGISTRATION"
                },
                "message": "Tourist registered successfully"
            }
        }
