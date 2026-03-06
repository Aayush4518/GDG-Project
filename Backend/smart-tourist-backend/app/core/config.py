import os
from typing import Optional


class Settings:
    """
    Application configuration settings
    """
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/smarttourist"
    )
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Tourist Safety System"
    
    # Security configuration (for future use)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Alternative frontend port
        "http://localhost:19006", # React Native Expo
    ]


settings = Settings()
