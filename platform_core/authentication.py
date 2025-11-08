"""
JWT Authentication Service

This module provides utilities for creating, encoding, and decoding
JSON Web Tokens (JWTs) for user authentication and authorization.
"""
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from platform_core.config import get_settings

class TokenData(BaseModel):
    """Schema for the data encoded in the JWT."""
    user_id: str
    tenant_id: str
    exp: datetime

def create_access_token(user_id: str, tenant_id: str, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    """
    Creates a new JWT access token.

    Args:
        user_id: The ID of the user.
        tenant_id: The ID of the tenant the user belongs to.
        expires_delta: The lifespan of the token.

    Returns:
        The encoded JWT as a string.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> TokenData | None:
    """
    Decodes and validates a JWT access token.

    Args:
        token: The JWT to decode.

    Returns:
        A TokenData object if the token is valid, otherwise None.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        # Pydantic will validate the payload structure
        return TokenData(**payload)
    except (jwt.PyJWTError, KeyError, TypeError):
        # Covers expired tokens, invalid signatures, and malformed payloads
        return None
