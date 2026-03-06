"""
CRUD operations for dashboard-related queries

This module contains complex database queries for providing dashboard data,
including efficient retrieval of tourists with their latest location information.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.sql import select
from ..db import models


def get_active_tourists_with_last_location(db: Session) -> List[Dict[str, Any]]:
    """
    Retrieve all active tourists with their most recent location data
    
    This function performs a complex query using window functions to efficiently
    get the latest location for each tourist. It's equivalent to this SQL:
    
    WITH LatestLocations AS (
        SELECT
            tourist_id,
            latitude,
            longitude,
            timestamp,
            ROW_NUMBER() OVER(PARTITION BY tourist_id ORDER BY timestamp DESC) as rn
        FROM location_logs
    )
    SELECT
        t.id as tourist_id,
        t.name,
        ll.latitude,
        ll.longitude,
        ll.timestamp
    FROM tourists t
    LEFT JOIN LatestLocations ll ON t.id = ll.tourist_id AND ll.rn = 1;
    
    Args:
        db: Database session
        
    Returns:
        List of dictionaries containing tourist data with their latest location
    """
    
    # Step 1: Create a subquery to get the latest location for each tourist
    # Using ROW_NUMBER() window function partitioned by tourist_id
    latest_locations_subquery = (
        db.query(
            models.LocationLog.tourist_id,
            models.LocationLog.latitude,
            models.LocationLog.longitude,
            models.LocationLog.timestamp,
            func.row_number().over(
                partition_by=models.LocationLog.tourist_id,
                order_by=desc(models.LocationLog.timestamp)
            ).label('rn')
        ).subquery('latest_locations')
    )
    
    # Step 2: Filter the subquery to only get rows where rn = 1 (most recent)
    latest_locations_filtered = (
        db.query(latest_locations_subquery)
        .filter(latest_locations_subquery.c.rn == 1)
        .subquery('latest_locations_filtered')
    )
    
    # Step 3: Join tourists with their latest locations
    query_result = (
        db.query(
            models.Tourist.id.label('tourist_id'),
            models.Tourist.name,
            latest_locations_filtered.c.latitude,
            latest_locations_filtered.c.longitude,
            latest_locations_filtered.c.timestamp
        )
        .outerjoin(
            latest_locations_filtered,
            models.Tourist.id == latest_locations_filtered.c.tourist_id
        )
        .all()
    )
    
    # Step 4: Format the results as a list of dictionaries
    results = []
    for row in query_result:
        tourist_data = {
            'tourist_id': row.tourist_id,
            'name': row.name,
            'last_known_location': None
        }
        
        # Only include location data if the tourist has location logs
        if row.latitude is not None and row.longitude is not None and row.timestamp is not None:
            tourist_data['last_known_location'] = {
                'latitude': row.latitude,
                'longitude': row.longitude,
                'timestamp': row.timestamp
            }
        
        results.append(tourist_data)
    
    return results


def get_tourist_location_history(db: Session, tourist_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get location history for a specific tourist
    
    This is a utility function that can be used for detailed tourist tracking
    or for debugging purposes.
    
    Args:
        db: Database session
        tourist_id: UUID of the tourist
        limit: Maximum number of location records to return
        
    Returns:
        List of location records for the tourist, ordered by timestamp DESC
    """
    location_history = (
        db.query(models.LocationLog)
        .filter(models.LocationLog.tourist_id == tourist_id)
        .order_by(desc(models.LocationLog.timestamp))
        .limit(limit)
        .all()
    )
    
    return [
        {
            'latitude': log.latitude,
            'longitude': log.longitude,
            'timestamp': log.timestamp
        }
        for log in location_history
    ]


def get_tourists_count_by_status(db: Session) -> Dict[str, int]:
    """
    Get count of tourists by different status categories
    
    This function provides summary statistics for dashboard analytics
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with counts of tourists by status
    """
    # Get total count of tourists
    total_tourists = db.query(models.Tourist).count()
    
    # Get count of tourists with location data (active)
    tourists_with_locations = (
        db.query(models.Tourist.id)
        .join(models.LocationLog, models.Tourist.id == models.LocationLog.tourist_id)
        .distinct()
        .count()
    )
    
    # Calculate tourists without location data
    tourists_without_locations = total_tourists - tourists_with_locations
    
    return {
        'total': total_tourists,
        'active_with_location': tourists_with_locations,
        'registered_no_location': tourists_without_locations
    }
