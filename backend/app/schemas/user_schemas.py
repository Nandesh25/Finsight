"""
FinSight — User API Schemas

Pydantic models for user-related API requests and responses.

Key Architecture Concepts:
    - DTOs (Data Transfer Objects): Separate API layer from domain layer
    - Request/Response Separation: Different schemas for input vs output
    - Validation: Pydantic automatically validates incoming data
    - Documentation: Field descriptions appear in OpenAPI/Swagger docs
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List


class UserCreateRequest(BaseModel):
    """
    Request schema for creating a new user.

    This is a DTO (Data Transfer Object) that defines what data
    the API expects when creating a user. Pydantic validates:
        - name and email are present
        - email is a valid email format
        - All required fields are provided
    """
    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }


class AccountSummary(BaseModel):
    """
    Summary of an account (nested in UserResponse).

    This provides minimal account information when returning user details.
    For full account details, clients should use the Account API.
    """
    account_number: str
    account_type: str
    balance: float

    class Config:
        json_schema_extra = {
            "example": {
                "account_number": "ACC-000001",
                "account_type": "savings",
                "balance": 1000.0
            }
        }


class UserResponse(BaseModel):
    """
    Response schema for a single user.

    This is what the API returns when creating or retrieving a user.
    It includes the user's accounts as nested objects.
    """
    user_id: str
    name: str
    email: str
    accounts: List[AccountSummary] = []
    total_balance: float

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USER-001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "accounts": [
                    {
                        "account_number": "ACC-000001",
                        "account_type": "savings",
                        "balance": 1000.0
                    }
                ],
                "total_balance": 1000.0
            }
        }


class UserListResponse(BaseModel):
    """
    Response schema for listing users.

    Returns a list of users with their basic information.
    """
    users: List[UserResponse]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "user_id": "USER-001",
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "accounts": [],
                        "total_balance": 0.0
                    }
                ],
                "count": 1
            }
        }
