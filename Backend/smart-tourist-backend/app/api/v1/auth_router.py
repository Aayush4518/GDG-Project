"""
Authentication and Registration API Router

This module provides API endpoints for tourist authentication and registration.
It serves as the entry point for new tourists and integrates with the ledger
service for tamper-evident registration logging.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any

# Database dependencies
from ...db.session import get_db

# Import CRUD operations
from ...crud import crud_tourist

# Import services
from ...services import ledger_service

# Import schemas
from ...schemas import tourist as schemas

# Import settings for credentials and secret key
from ...core.config import settings

# Create router instance
router = APIRouter(prefix="/auth", tags=["Authentication & Registration"])

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours


# --------------------------------------------------------------------------- #
#  Authority (dashboard) login                                                 #
# --------------------------------------------------------------------------- #

class AuthorityLoginRequest(BaseModel):
    username: str
    password: str


class AuthorityLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


@router.post("/authority/login", response_model=AuthorityLoginResponse)
async def authority_login(credentials: AuthorityLoginRequest) -> AuthorityLoginResponse:
    """
    Login endpoint for dashboard authorities (Police / Tourism officers).

    Validates credentials against environment-configured accounts and returns
    a signed JWT token that the dashboard must include in subsequent requests
    via the Authorization: Bearer <token> header.
    """
    username = credentials.username.strip().lower()
    password = credentials.password

    if username == settings.POLICE_USERNAME.lower() and password == settings.POLICE_PASSWORD:
        role = "Police"
    elif username == settings.TOURISM_USERNAME.lower() and password == settings.TOURISM_PASSWORD:
        role = "Tourism"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

    return AuthorityLoginResponse(access_token=token, role=role, username=username)


@router.post("/register", response_model=schemas.RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_tourist(
    tourist_data: schemas.TouristCreate,
    db: Session = Depends(get_db)
) -> schemas.RegistrationResponse:
    """
    Register a new tourist in the Smart Tourist Safety System
    
    This endpoint creates a new tourist record in the database and logs
    the registration event to the tamper-evident ledger for audit purposes.
    It serves as the primary entry point for mobile app user registration.
    
    **Integration Points:**
    - Creates tourist record via CRUD layer
    - Logs registration to tamper-evident ledger
    - Returns registration confirmation with ledger proof
    
    Args:
        tourist_data: Tourist registration data from request body
        db: Database session dependency
        
    Returns:
        RegistrationResponse: Confirmation with tourist ID and ledger entry
        
    Raises:
        HTTPException: 400 if tourist already exists, 500 if creation fails
        
    Example Request:
        ```json
        {
            "name": "Alice Johnson",
            "kyc_hash": "kyc_abc123def456",
            "emergency_contact": {
                "name": "John Johnson",
                "phone": "+1234567890",
                "email": "emergency@example.com"
            },
            "trip_end_date": "2025-09-22T18:00:00Z"
        }
        ```
        
    Example Response:
        ```json
        {
            "tourist_id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Alice Johnson",
            "ledger_entry": {
                "block_id": 1001,
                "hash": "a1b2c3d4e5f6...",
                "timestamp": "2025-09-15T14:30:00.123456Z",
                "event": "REGISTRATION"
            },
            "message": "Tourist registered successfully"
        }
        ```
    """
    try:
        # Step 1: Check if tourist with this KYC hash already exists
        existing_tourist = crud_tourist.get_tourist_by_kyc_hash(db, tourist_data.kyc_hash)
        if existing_tourist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tourist with KYC hash '{tourist_data.kyc_hash}' already registered"
            )
        
        # Step 2: Create the new tourist record using CRUD layer
        new_tourist = crud_tourist.create_tourist(db, tourist_data)
        
        # Step 3: CRITICAL INTEGRATION - Log registration to tamper-evident ledger
        event_data = {
            "event": "REGISTRATION",
            "name": new_tourist.name,
            "kyc_hash": new_tourist.kyc_hash,
            "registered_at": new_tourist.created_at.isoformat(),
            "trip_end_date": new_tourist.trip_end_date.isoformat()
        }
        
        # Call the existing ledger service to create tamper-evident record
        ledger_block = ledger_service.add_new_block(
            db=db,
            tourist_id=str(new_tourist.id),  # Convert UUID to string
            event_data=event_data
        )
        
        # Step 4: Construct the response with ledger entry details
        ledger_entry = schemas.LedgerEntry(
            block_id=ledger_block.id,
            hash=ledger_block.current_hash,
            timestamp=ledger_block.timestamp,
            event="REGISTRATION"
        )
        
        # Step 5: Return the registration response
        return schemas.RegistrationResponse(
            tourist_id=new_tourist.id,
            name=new_tourist.name,
            ledger_entry=ledger_entry,
            message="Tourist registered successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate tourist)
        raise
    except Exception as e:
        # Handle any other errors during registration
        db.rollback()  # Rollback any partial database changes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/tourist/{tourist_id}", response_model=Dict[str, Any])
async def get_tourist_info(
    tourist_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve tourist information by ID
    
    This endpoint provides tourist details for authentication verification
    and profile management. It's used by mobile apps to verify registration
    status and retrieve basic tourist information.
    
    Args:
        tourist_id: UUID string of the tourist
        db: Database session dependency
        
    Returns:
        Dict containing tourist information
        
    Raises:
        HTTPException: 404 if tourist not found
    """
    try:
        # Retrieve tourist from database
        tourist = crud_tourist.get_tourist(db, tourist_id)
        
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tourist with ID '{tourist_id}' not found"
            )
        
        # Return tourist information (excluding sensitive data)
        return {
            "tourist_id": str(tourist.id),
            "name": tourist.name,
            "created_at": tourist.created_at.isoformat(),
            "trip_end_date": tourist.trip_end_date.isoformat(),
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tourist information: {str(e)}"
        )


@router.patch("/tourist/{tourist_id}/emergency-contact")
async def update_emergency_contact(
    tourist_id: str,
    emergency_contact: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update tourist's emergency contact information
    
    This endpoint allows tourists to update their emergency contact
    information through the mobile app for safety purposes.
    
    Args:
        tourist_id: UUID string of the tourist
        emergency_contact: New emergency contact information
        db: Database session dependency
        
    Returns:
        Dict with update confirmation
        
    Raises:
        HTTPException: 404 if tourist not found, 500 if update fails
    """
    try:
        # Update emergency contact
        updated_tourist = crud_tourist.update_tourist_emergency_contact(
            db, tourist_id, emergency_contact
        )
        
        if not updated_tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tourist with ID '{tourist_id}' not found"
            )
        
        return {
            "tourist_id": tourist_id,
            "message": "Emergency contact updated successfully",
            "updated_at": updated_tourist.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update emergency contact: {str(e)}"
        )
