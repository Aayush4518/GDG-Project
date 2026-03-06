"""
Simple test server for API validation using SQLite
"""

import os
import tempfile
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create temporary SQLite database
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db.close()
os.environ['DATABASE_URL'] = f"sqlite:///{temp_db.name}"

print(f"✅ Using SQLite database: {temp_db.name}")

# Import FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import dashboard_router, ledger_router, notification_router, auth_router
from app.db.base import Base
from app.db.session import engine

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Initialize FastAPI application
app = FastAPI(
    title="Smart Tourist Safety System - Test Mode",
    description="A tamper-evident safety monitoring system for tourists with real-time alerting",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(ledger_router.router, prefix="/api/v1", tags=["Internal APIs"])
app.include_router(notification_router.router, prefix="/api/v1", tags=["Internal APIs"])
app.include_router(auth_router.router, prefix="/api/v1", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Smart Tourist Safety System API - Test Mode", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "sqlite"}

if __name__ == "__main__":
    print("🚀 Starting FastAPI server in test mode...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
