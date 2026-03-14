from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os

# Prefer DATABASE_URL from environment (set by docker-compose or .env).
# Default includes explicit port 5432 to be consistent with config.py.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/smarttourist")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
