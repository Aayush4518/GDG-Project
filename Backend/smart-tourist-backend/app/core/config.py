import os
import warnings
from dotenv import load_dotenv

load_dotenv()

_INSECURE_SECRETS = {
    "your-secret-key-here",
    "change-me-generate-a-strong-secret-key-before-running",
}


class Settings:
    """
    Application configuration settings.
    All sensitive values are loaded from environment variables or a .env file.
    """

    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/smarttourist"
    )

    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Tourist Safety System"

    # Security configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-generate-a-strong-secret-key-before-running")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Authority (dashboard) credentials — loaded from environment
    POLICE_USERNAME: str = os.getenv("POLICE_USERNAME", "police@travelguardian.gov")
    POLICE_PASSWORD: str = os.getenv("POLICE_PASSWORD", "police123")
    TOURISM_USERNAME: str = os.getenv("TOURISM_USERNAME", "tourism@travelguardian.gov")
    TOURISM_PASSWORD: str = os.getenv("TOURISM_PASSWORD", "tourism123")

    # CORS — specify exact allowed origins; never use ["*"] in production
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite default
        "http://localhost:5174",   # Vite alternate (dashboard)
        "http://localhost:8080",   # Alternative frontend
        "http://localhost:8081",   # Expo web
        "http://localhost:8083",   # Expo web alternate
        "http://localhost:19000",  # Expo dev tools
        "http://localhost:19006",  # React Native Expo web
    ]

    def __init__(self):
        if self.SECRET_KEY in _INSECURE_SECRETS:
            warnings.warn(
                "SECRET_KEY is set to an insecure default. "
                "Set a strong SECRET_KEY in your .env file before deploying.",
                RuntimeWarning,
                stacklevel=2,
            )


settings = Settings()
