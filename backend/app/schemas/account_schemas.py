"""
FinSight — Account API Schemas

Pydantic models for account-related API requests and responses.

Key Architecture Concepts:
    - Request Validation: Pydantic validates input before it reaches business logic
    - Separation of Concerns: API schemas separate from domain models
    - Type Safety: Clear type definitions for API contracts
"""

from pydantic import BaseModel, Field
from typing import Literal


class AccountCreateRequest(BaseModel):
    """
    Request schema for creating a new account.

    The user_id is required to associate the account with a user.
    Account type is restricted to 'savings' or 'checking' using Literal.
    """
    user_id: str = Field(..., description="ID of the user who will own this account")
    account_type: Literal["savings", "checking"] = Field(
        ...,
        description="Type of account (savings or checking)"
    )
    initial_balance: float = Field(
        default=0.0,
        ge=0.0,
        description="Initial balance (must be non-negative)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USER-001",
                "account_type": "savings",
                "initial_balance": 1000.0
            }
        }


class AccountResponse(BaseModel):
    """
    Response schema for account operations.

    Returns complete account information including current balance.
    """
    account_number: str
    account_type: str
    balance: float
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "account_number": "ACC-000001",
                "account_type": "savings",
                "balance": 1000.0,
                "user_id": "USER-001"
            }
        }


class DepositRequest(BaseModel):
    """
    Request schema for depositing money into an account.

    Validates that the amount is positive.
    """
    amount: float = Field(..., gt=0.0, description="Amount to deposit (must be positive)")
    description: str = Field(default="", max_length=500, description="Optional transaction description")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 500.0,
                "description": "Salary deposit"
            }
        }


class WithdrawRequest(BaseModel):
    """
    Request schema for withdrawing money from an account.

    Validates that the amount is positive.
    Actual balance checking happens in the domain layer.
    """
    amount: float = Field(..., gt=0.0, description="Amount to withdraw (must be positive)")
    description: str = Field(default="", max_length=500, description="Optional transaction description")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 200.0,
                "description": "ATM withdrawal"
            }
        }


class BalanceResponse(BaseModel):
    """
    Response schema for balance queries.

    Simple response containing current account balance.
    """
    account_number: str
    balance: float

    class Config:
        json_schema_extra = {
            "example": {
                "account_number": "ACC-000001",
                "balance": 800.0
            }
        }


class TransactionResult(BaseModel):
    """
    Response schema for deposit/withdraw operations.

    Returns transaction details and new balance.
    """
    transaction_id: str
    account_number: str
    transaction_type: str
    amount: float
    new_balance: float
    description: str
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-000001",
                "account_number": "ACC-000001",
                "transaction_type": "deposit",
                "amount": 500.0,
                "new_balance": 1500.0,
                "description": "Salary deposit",
                "timestamp": "2026-09-02T15:42:45.468Z"
            }
        }
