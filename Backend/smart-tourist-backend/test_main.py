"""
Simplified test setup with SQLite for testing tourist registration API
without requiring PostgreSQL installation.
"""

import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

# Create a temporary SQLite database for testing
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db.close()

# Override database URL for testing
os.environ['DATABASE_URL'] = f"sqlite:///{temp_db.name}"

# Import after setting environment variable
from app.db.session import engine, SessionLocal

# Create all tables
Base.metadata.create_all(bind=engine)

print(f"✅ Test database created at: {temp_db.name}")
print("✅ All tables created successfully")
print("🚀 Starting FastAPI server with SQLite backend...")

# Now start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
