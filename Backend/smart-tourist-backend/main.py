from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.core.config import settings
from app.api.v1 import dashboard_router
from app.api.v1 import ledger_router
from app.api.v1 import notification_router
from app.api.v1 import auth_router
from app.api.v1 import tourist_router
from app.api.v1 import risk_router
from app.db.base import Base
from app.db.session import engine
from app.services.anomaly_service import run_anomaly_checks_periodically, get_anomaly_detection_status

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Smart Tourist Safety System",
    description="A tamper-evident safety monitoring system for tourists with real-time alerting",
    version="1.0.0"
)

# Configure CORS — restrict to known frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the dashboard router for WebSocket connections
app.include_router(dashboard_router.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

# Include the internal ledger API router for Auth & Location services
app.include_router(ledger_router.router, prefix="/api/v1", tags=["Internal APIs"])

# Include the internal notification API router for Auth & Location services
app.include_router(notification_router.router, prefix="/api/v1", tags=["Internal APIs"])

# Include the authentication and registration router for tourist management
app.include_router(auth_router.router, prefix="/api/v1", tags=["Authentication"])

# Include the tourist tracking and panic alert router for location data and emergency response
app.include_router(tourist_router.router, prefix="/api/v1", tags=["Tourist Tracking"])

# Include the ML-powered risk prediction router
app.include_router(risk_router.router, prefix="/api/v1", tags=["Risk Prediction"])


@app.on_event("startup")
async def startup_event():
    """
    Initialize background tasks on application startup
    """
    print("🚀 Starting Smart Tourist Safety System")
    print("🔍 Launching anomaly detection background task...")
    
    # Start the anomaly detection background task
    asyncio.create_task(run_anomaly_checks_periodically())
    
    print("✅ Anomaly detection system initialized")


@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "Smart Tourist Safety System API",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Tourist Registration & Authentication",
            "Real-time Location Tracking",
            "Panic Button Emergency Alerts",
            "Text-based Emergency Alerts (Multilingual)",
            "E-FIR Generation for Law Enforcement",
            "Heuristic Anomaly Detection Engine",
            "Tamper-evident Blockchain Ledger",
            "WebSocket Dashboard for Monitoring"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy"}


@app.get("/anomaly-status")
async def anomaly_detection_status():
    """
    Get current status of the anomaly detection system
    """
    return get_anomaly_detection_status()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
