"""
FinSight — Authentication API Schemas

Pydantic models for authentication-related API requests and responses.

Key Architecture Concepts:
    - DTOs (Data Transfer Objects): Separate API layer from domain layer
    - Request/Response Separation: Different schemas for input vs output
    - Validation: Pydantic automatically validates incoming data
    - Security: Password fields excluded from response schemas
"""

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """
    Request schema for user registration.

    This is what the API expects when a new user signs up.
    Note: Password is sent in plain text over HTTPS, then immediately hashed.
    """
    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password (min 8 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        }


class UserLoginRequest(BaseModel):
    """
    Request schema for user login.

    Uses email and password for authentication.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    """
    Response schema for authentication endpoints.

    Returns a JWT access token that the client must include
    in subsequent requests to authenticate.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    user_id: str = Field(..., description="ID of the authenticated user")
    role: str = Field(..., description="User's role (USER or ADMIN)")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "USER-001",
                "role": "USER"
            }
        }


class AuthErrorResponse(BaseModel):
    """
    Response schema for authentication errors.

    Standard error format for authentication failures.
    """
    detail: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials"
            }
        }
