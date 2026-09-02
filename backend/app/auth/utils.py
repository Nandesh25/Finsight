"""
FinSight — Authentication Utilities

This module provides security utilities for password hashing and JWT token management.

Key Security Concepts:
    - Password Hashing: Never store plain-text passwords
    - JWT (JSON Web Tokens): Stateless authentication tokens
    - Token Expiration: Security through time-limited access
    - Secret Key: Used to sign and verify tokens

Architecture:
    - Encapsulation: Security logic isolated from business logic
    - Single Responsibility: Each function has one clear purpose
    - Abstraction: Hide complexity of bcrypt and JWT libraries
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# Password hashing context using bcrypt
# CryptContext is a facade pattern — it provides a simple interface
# to the complex bcrypt hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
# In production, these should come from environment variables
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Bcrypt is a one-way hashing function designed for passwords:
        - Computationally expensive (slow by design)
        - Includes a random salt automatically
        - Cannot be reversed to get the original password

    This demonstrates the principle of *never storing plain-text passwords*.

    Args:
        password: Plain-text password to hash

    Returns:
        Hashed password string (safe to store in database)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.

    This is how we check if a user's login password is correct.
    We never compare plain-text passwords directly.

    Args:
        plain_password: The password the user entered
        hashed_password: The hashed password from the database

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    JWT (JSON Web Token) is a standard for creating access tokens that contain:
        - Header: Token type and signing algorithm
        - Payload: User data (called "claims")
        - Signature: Cryptographic signature to prevent tampering

    Key concepts:
        - Stateless: Server doesn't need to store session data
        - Self-contained: Token contains all necessary user information
        - Signed: Cannot be tampered with without detection
        - Expiring: Security through time-limited access

    Args:
        data: Dictionary of data to encode in the token (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    # Copy the data so we don't modify the original
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add expiration to the token payload
    to_encode.update({"exp": expire})

    # Create and return the encoded JWT
    # The SECRET_KEY is used to sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.

    This function:
        1. Verifies the token signature (prevents tampering)
        2. Checks if the token has expired
        3. Extracts the payload data

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload as a dictionary, or None if invalid

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        # Decode the token using the same SECRET_KEY and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Token is invalid, expired, or tampered with
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract the user ID from a JWT token.

    JWT convention uses "sub" (subject) claim for the user identifier.

    Args:
        token: JWT token string

    Returns:
        User ID from the token, or None if token is invalid
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    # Extract the "sub" (subject) claim which contains the user_id
    user_id: Optional[str] = payload.get("sub")
    return user_id
