"""Runtime risk model prediction service."""

from datetime import datetime
from typing import Dict, List, Optional
import logging

import numpy as np

from .feature_engineering import FEATURE_COLUMNS, build_live_features, parse_timestamp
from .model_loader import get_model_bundle

logger = logging.getLogger(__name__)


def _danger_level(risk_score: float) -> str:
    if risk_score >= 0.75:
        return "HIGH"
    if risk_score >= 0.40:
        return "MEDIUM"
    return "LOW"


def _heuristic_score(features: Dict[str, float]) -> float:
    """Fallback score when model is unavailable."""
    hour = features["hour_of_day"]
    nearby = features["nearby_alert_density"]
    historical = features["historical_alert_count"]
    lighting = features["lighting_index"]

    score = 0.10
    if hour >= 21 or hour <= 4:
        score += 0.30

    score += min(0.35, nearby * 0.03)
    score += min(0.25, historical * 0.01)
    score += (1.0 - lighting) * 0.15
    return float(max(0.0, min(1.0, score)))


def predict_risk(
    latitude: float,
    longitude: float,
    timestamp: Optional[str | datetime] = None,
    db=None,
) -> Dict[str, float | str]:
    """Predict risk score and danger level for one coordinate."""
    ts = parse_timestamp(timestamp)
    feature_map = build_live_features(db=db, latitude=latitude, longitude=longitude, timestamp=ts)
    feature_array = np.array([[feature_map[column] for column in FEATURE_COLUMNS]], dtype=float)

    bundle = get_model_bundle()
    if bundle is None:
        risk_score = _heuristic_score(feature_map)
        return {"risk_score": risk_score, "danger_level": _danger_level(risk_score)}

    model = bundle["model"]
    risk_score = 0.0
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(feature_array)[0]
        if len(probabilities) == 2:
            risk_score = float(probabilities[1])
        else:
            risk_score = float(np.max(probabilities))
    else:
        prediction = model.predict(feature_array)[0]
        risk_score = 1.0 if int(prediction) == 1 else 0.0

    risk_score = float(max(0.0, min(1.0, risk_score)))
    return {"risk_score": risk_score, "danger_level": _danger_level(risk_score)}


def predict_heatmap(
    bbox: List[float],
    timestamp: Optional[str | datetime] = None,
    db=None,
    rows: int = 10,
    cols: int = 10,
) -> List[Dict[str, float]]:
    """Return grid-based risk scores for a viewport bounding box."""
    if len(bbox) != 4:
        raise ValueError("bbox must be [min_lat, min_lon, max_lat, max_lon]")

    min_lat, min_lon, max_lat, max_lon = bbox
    if min_lat >= max_lat or min_lon >= max_lon:
        raise ValueError("Invalid bbox bounds")

    ts = parse_timestamp(timestamp)

    lat_step = (max_lat - min_lat) / rows
    lon_step = (max_lon - min_lon) / cols

    points: List[Dict[str, float]] = []
    for i in range(rows):
        for j in range(cols):
            lat = min_lat + (i + 0.5) * lat_step
            lon = min_lon + (j + 0.5) * lon_step
            prediction = predict_risk(latitude=lat, longitude=lon, timestamp=ts, db=db)
            points.append(
                {
                    "lat": float(lat),
                    "lon": float(lon),
                    "risk_score": float(prediction["risk_score"]),
                }
            )

    return points
