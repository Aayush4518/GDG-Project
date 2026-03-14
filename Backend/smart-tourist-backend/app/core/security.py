"""
JWT authentication helpers and FastAPI dependencies.

Dashboard endpoints (active-tourists, analytics, details, E-FIR, etc.) must be
protected with the `require_authority` dependency so only logged-in Police /
Tourism officers can access tourist PII.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from typing import Dict, Any

from .config import settings

ALGORITHM = "HS256"

_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_authority(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """
    FastAPI dependency — validates the Bearer JWT token issued by
    POST /api/v1/auth/authority/login.

    Usage:
        @router.get("/protected")
        def protected(user=Depends(require_authority)):
            return {"role": user["role"]}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode_token(credentials.credentials)


def require_police(user: Dict[str, Any] = Depends(require_authority)) -> Dict[str, Any]:
    """Restrict endpoint to Police role only."""
    if user.get("role") != "Police":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Police role required for this action.",
        )
    return user
