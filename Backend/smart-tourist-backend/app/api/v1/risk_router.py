"""Risk prediction APIs backed by ML model inference."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...ml.risk_model import predict_heatmap, predict_risk
from ...schemas.risk import HeatmapPoint, HeatmapRequest, RiskPredictRequest, RiskPredictResponse

router = APIRouter(prefix="/risk", tags=["Risk Prediction"])


@router.post("/predict", response_model=RiskPredictResponse)
async def get_risk_prediction(
    latitude: float | None = Query(None, description="Latitude"),
    longitude: float | None = Query(None, description="Longitude"),
    timestamp: datetime | None = Query(None, description="ISO timestamp"),
    payload: RiskPredictRequest | None = Body(None),
    db: Session = Depends(get_db),
) -> RiskPredictResponse:
    """Predict risk score and danger level for a coordinate at a given timestamp."""
    try:
        if payload is None and (latitude is None or longitude is None or timestamp is None):
            raise HTTPException(
                status_code=400,
                detail="Provide either request body or query parameters: latitude, longitude, timestamp",
            )

        source = payload or RiskPredictRequest(
            latitude=latitude, longitude=longitude, timestamp=timestamp
        )
        prediction = predict_risk(
            latitude=source.latitude,
            longitude=source.longitude,
            timestamp=source.timestamp,
            db=db,
        )
        return RiskPredictResponse(**prediction)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to predict risk: {exc}")


@router.get("/heatmap", response_model=List[HeatmapPoint])
async def get_risk_heatmap(
    bbox: str | None = Query(None, description="min_lat,min_lon,max_lat,max_lon"),
    timestamp: datetime | None = Query(None, description="ISO timestamp (optional)"),
    rows: int = Query(10, ge=2, le=50),
    cols: int = Query(10, ge=2, le=50),
    payload: HeatmapRequest | None = Body(None),
    db: Session = Depends(get_db),
) -> List[HeatmapPoint]:
    """Return grid-based risk scores for the requested viewport bbox."""
    try:
        if payload is not None:
            bounds = payload.bbox
            ts = payload.timestamp or datetime.now(timezone.utc)
        else:
            if not bbox:
                raise HTTPException(
                    status_code=400,
                    detail="Provide either request body or query parameter: bbox",
                )
            bounds = [float(value.strip()) for value in bbox.split(",")]
            ts = timestamp or datetime.now(timezone.utc)

        points = predict_heatmap(
            bbox=bounds,
            timestamp=ts,
            db=db,
            rows=rows,
            cols=cols,
        )
        return [HeatmapPoint(**point) for point in points]
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to build risk heatmap: {exc}")
