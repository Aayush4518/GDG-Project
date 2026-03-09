"""Schemas for ML risk APIs."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class RiskPredictResponse(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    danger_level: str


class RiskPredictRequest(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime


class HeatmapRequest(BaseModel):
    bbox: List[float] = Field(..., min_length=4, max_length=4)
    timestamp: datetime | None = None


class HeatmapPoint(BaseModel):
    lat: float
    lon: float
    risk_score: float = Field(..., ge=0.0, le=1.0)


class HeatmapResponse(BaseModel):
    points: List[HeatmapPoint]


class RiskPredictQuery(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
