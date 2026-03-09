"""Feature engineering utilities for geographic risk prediction."""

from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db import models

FEATURE_COLUMNS: List[str] = [
    "latitude",
    "longitude",
    "hour_of_day",
    "day_of_week",
    "nearby_alert_density",
    "historical_alert_count",
    "crowd_density",
    "lighting_index",
]


def parse_timestamp(timestamp: Optional[str | datetime] = None) -> datetime:
    """Normalize incoming timestamp into datetime."""
    if timestamp is None:
        return datetime.utcnow()
    if isinstance(timestamp, datetime):
        return timestamp

    normalized = timestamp.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in meters between two coordinates."""
    r = 6371000.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def _count_nearby_location_logs(
    db: Session,
    latitude: float,
    longitude: float,
    since: datetime,
    radius_meters: float,
) -> int:
    """Count location logs in a radius since a given timestamp (proxy for alert density)."""
    lat_delta = radius_meters / 111320.0
    lon_delta = radius_meters / (111320.0 * max(0.1, cos(radians(latitude))))

    candidate_logs = (
        db.query(models.LocationLog)
        .filter(models.LocationLog.timestamp >= since)
        .filter(models.LocationLog.latitude.between(latitude - lat_delta, latitude + lat_delta))
        .filter(models.LocationLog.longitude.between(longitude - lon_delta, longitude + lon_delta))
        .all()
    )

    return sum(
        1
        for row in candidate_logs
        if haversine_distance_m(latitude, longitude, row.latitude, row.longitude) <= radius_meters
    )


def build_feature_vector(
    latitude: float,
    longitude: float,
    timestamp: datetime,
    nearby_alert_density: float,
    historical_alert_count: float,
    crowd_density: float = 0.5,
    lighting_index: Optional[float] = None,
) -> Dict[str, float]:
    """Build a single model-ready feature vector."""
    hour_of_day = float(timestamp.hour)
    day_of_week = float(timestamp.weekday())

    if lighting_index is None:
        # Placeholder approximation: brighter between 6am and 6pm.
        lighting_index = 0.9 if 6 <= timestamp.hour <= 18 else 0.2

    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "nearby_alert_density": float(nearby_alert_density),
        "historical_alert_count": float(historical_alert_count),
        "crowd_density": float(crowd_density),
        "lighting_index": float(lighting_index),
    }


def build_live_features(
    db: Optional[Session],
    latitude: float,
    longitude: float,
    timestamp: datetime,
    crowd_density: float = 0.5,
    lighting_index: Optional[float] = None,
) -> Dict[str, float]:
    """Compute live features from current coordinate and DB history."""
    nearby_alert_density = 0.0
    historical_alert_count = 0.0

    if db is not None:
        nearby_alert_density = float(
            _count_nearby_location_logs(
                db=db,
                latitude=latitude,
                longitude=longitude,
                since=timestamp - timedelta(hours=24),
                radius_meters=1000.0,
            )
        )
        historical_alert_count = float(
            _count_nearby_location_logs(
                db=db,
                latitude=latitude,
                longitude=longitude,
                since=timestamp - timedelta(days=30),
                radius_meters=1500.0,
            )
        )

    return build_feature_vector(
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
        nearby_alert_density=nearby_alert_density,
        historical_alert_count=historical_alert_count,
        crowd_density=crowd_density,
        lighting_index=lighting_index,
    )
