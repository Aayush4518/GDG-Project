from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Response
from typing import List
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...db import models
from ...services import ledger_service
from ...services import efir_service
from ...services.websocket_manager import ConnectionManager
from ...crud import crud_dashboard
from ...schemas import tourist as schemas

# Create router instance
router = APIRouter()

# Create a single, shared instance of the connection manager
manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for dashboard clients to receive real-time alerts and updates
    
    Args:
        websocket: The WebSocket connection from the dashboard client
    """
    # Accept the connection and add it to active connections
    await manager.connect(websocket)
    
    try:
        # Keep the connection alive and listen for any potential incoming messages
        # (though for now we are primarily broadcasting out)
        while True:
            # This receives any text message to keep the connection alive
            # In the future, this could handle commands from the dashboard
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        # Client disconnected normally
        pass
    except Exception:
        # Any other exception occurred
        pass
    finally:
        # Ensure the connection is removed from active connections
        manager.disconnect(websocket)


@router.get("/ledger/verify", status_code=200)
def verify_ledger_integrity(db: Session = Depends(get_db)):
    """
    Endpoint to verify the integrity of the tamper-evident ledger chain
    
    This endpoint runs the chain verification logic and returns a clear
    success or failure status for demonstration purposes.
    
    Args:
        db: Database session dependency
        
    Returns:
        JSON response indicating whether the ledger chain is valid or tampered
    """
    try:
        # Call the ledger service to verify chain integrity
        is_valid = ledger_service.verify_chain(db)
        
        if is_valid:
            return {
                "status": "success",
                "message": "Ledger integrity verified. No tampering detected."
            }
        else:
            return {
                "status": "error", 
                "message": "CRITICAL: Ledger tampering detected! Chain is invalid."
            }
            
    except Exception as e:
        # Handle any unexpected errors during verification
        return {
            "status": "error",
            "message": f"Error during ledger verification: {str(e)}"
        }


@router.get("/active-tourists", response_model=List[schemas.TouristStatus])
def get_active_tourists(db: Session = Depends(get_db)):
    """
    Get all active tourists with their last known location for dashboard initialization
    
    This endpoint provides the complete initial state for the authorities' dashboard,
    showing all registered tourists and their most recent location data. The dashboard
    uses this for initial map population, then relies on WebSocket for real-time updates.
    
    Args:
        db: Database session dependency
        
    Returns:
        List of TouristStatus objects containing tourist info and last known location
    """
    try:
        # Get tourists with their latest location data using complex query
        tourist_data = crud_dashboard.get_active_tourists_with_last_location(db)
        
        # Convert to response format
        result = []
        for data in tourist_data:
            tourist_status = schemas.TouristStatus(
                tourist_id=data['tourist_id'],
                name=data['name'],
                last_known_location=data['last_known_location'],
                status="active"
            )
            result.append(tourist_status)
        
        return result
        
    except Exception as e:
        # In case of error, return empty list with error logged
        # In production, you'd want proper logging here
        print(f"Error fetching active tourists: {str(e)}")
        return []


@router.get("/tourists/{tourist_id}/details", response_model=schemas.TouristDetails)
def get_tourist_details(tourist_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific tourist including location history
    
    This endpoint provides comprehensive tourist data for detailed dashboard views,
    including their complete location tracking history. Useful for authorities
    to analyze movement patterns and investigate specific tourist activities.
    
    Args:
        tourist_id: UUID string of the tourist to retrieve details for
        db: Database session dependency
        
    Returns:
        TouristDetails object with tourist info and location history
        
    Raises:
        HTTPException: 404 if tourist not found
    """
    try:
        # First, get the tourist's basic information
        tourist = db.query(models.Tourist).filter(models.Tourist.id == tourist_id).first()
        
        if not tourist:
            raise HTTPException(
                status_code=404, 
                detail=f"Tourist with ID {tourist_id} not found"
            )
        
        # Get the tourist's location history (limit to last 50 for performance)
        location_history_data = crud_dashboard.get_tourist_location_history(
            db=db, 
            tourist_id=tourist_id, 
            limit=50
        )
        
        # Convert location history to LocationBase objects
        location_history = [
            schemas.LocationBase(
                latitude=loc['latitude'],
                longitude=loc['longitude'],
                timestamp=loc['timestamp']
            )
            for loc in location_history_data
        ]
        
        # Return the detailed tourist information
        return schemas.TouristDetails(
            tourist_id=tourist.id,
            name=tourist.name,
            location_history=location_history
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tourist details: {str(e)}"
        )


@router.get("/analytics", response_model=schemas.DashboardAnalytics)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    """
    Get dashboard analytics and summary statistics
    
    This endpoint provides overview statistics for the authorities' dashboard,
    showing counts of tourists by different status categories. Essential for
    situational awareness and resource allocation decisions.
    
    Args:
        db: Database session dependency
        
    Returns:
        DashboardAnalytics object with tourist counts by status
    """
    try:
        # Get tourist counts by status from existing CRUD function
        analytics_data = crud_dashboard.get_tourists_count_by_status(db)
        
        # Return the analytics data - FastAPI will validate against schema
        return schemas.DashboardAnalytics(
            total=analytics_data['total'],
            active_with_location=analytics_data['active_with_location'],
            registered_no_location=analytics_data['registered_no_location']
        )
        
    except Exception as e:
        # Handle any errors and return default analytics
        # In production, you'd want proper logging here
        print(f"Error fetching dashboard analytics: {str(e)}")
        return schemas.DashboardAnalytics(
            total=0,
            active_with_location=0,
            registered_no_location=0
        )


@router.post("/tourists/{tourist_id}/generate-efir")
async def generate_efir_for_tourist(
    tourist_id: str,
    db: Session = Depends(get_db)
) -> Response:
    """
    Generate an automated E-FIR (Electronic First Information Report) PDF for a missing tourist
    
    This endpoint creates a comprehensive PDF report that law enforcement can use
    as a preliminary FIR for missing tourist cases. The report includes verified
    tourist information, location tracking history, and tamper-evident ledger data.
    
    **Key Features:**
    - Comprehensive tourist details and emergency contacts
    - Last known location history with GPS coordinates
    - Tamper-evident blockchain verification
    - Professional formatting for law enforcement use
    - Automated filename generation with timestamps
    
    Args:
        tourist_id: UUID string of the tourist for E-FIR generation
        db: Database session dependency
        
    Returns:
        Response: PDF file download with appropriate headers
        
    Raises:
        HTTPException: 404 if tourist not found, 500 if PDF generation fails
        
    Example Response Headers:
        Content-Type: application/pdf
        Content-Disposition: attachment; filename="EFIR_12345678_20250915_143000.pdf"
        
    Example Usage:
        POST /api/v1/dashboard/tourists/123e4567-e89b-12d3/generate-efir
        → Downloads: EFIR_123E4567_20250915_143000.pdf
    """
    try:
        # Generate the E-FIR PDF content
        pdf_content = efir_service.generate_efir_pdf(db, tourist_id)
        
        # Generate standardized filename
        filename = efir_service.get_efir_filename(tourist_id)
        
        # Return PDF as downloadable response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            }
        )
        
    except ValueError as e:
        # Tourist not found or validation error
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        # PDF generation or other errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate E-FIR: {str(e)}"
        )


# Risk Zones Endpoint
@router.get("/risk-zones")
def get_risk_zones(db: Session = Depends(get_db)):
    """
    Get risk zones for map display with coordinates and risk levels
    
    This endpoint provides risk zone polygons for the dashboard map visualization,
    showing areas that authorities have identified as high-risk for tourists.
    
    Args:
        db: Database session dependency
        
    Returns:
        List of risk zone objects with coordinates and risk levels
    """
    try:
        # Query risk zones from database
        risk_zones = db.query(models.HighRiskZone).all()
        
        # Convert to response format - simplified for demonstration
        result = []
        for zone in risk_zones:
            # For now, return sample risk zones since we don't have actual data
            # In production, you'd extract coordinates from zone.geometry
            pass
        
        # Return sample risk zones for testing
        return [
            {
                "id": "zone_1",
                "coordinates": [
                    {"latitude": 25.5941, "longitude": 85.1376},
                    {"latitude": 25.5941, "longitude": 85.1476},
                    {"latitude": 25.6041, "longitude": 85.1476},
                    {"latitude": 25.6041, "longitude": 85.1376}
                ],
                "level": "high"
            },
            {
                "id": "zone_2", 
                "coordinates": [
                    {"latitude": 26.1445, "longitude": 91.7362},
                    {"latitude": 26.1445, "longitude": 91.7462},
                    {"latitude": 26.1545, "longitude": 91.7462},
                    {"latitude": 26.1545, "longitude": 91.7362}
                ],
                "level": "medium"
            }
        ]
        
    except Exception as e:
        # Return empty array on error - risk zones are optional
        print(f"Error fetching risk zones: {str(e)}")
        return []


# The manager instance is exported at module level for use by alert_service
# This allows the centralized alert service to import and use the manager directly
