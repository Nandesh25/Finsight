"""
FinSight — API Schemas

This package contains Pydantic schemas for API request/response validation.
These are DTOs (Data Transfer Objects) that define the shape of data
going in and out of the API.
"""

from app.schemas.user_schemas import (
    UserCreateRequest,
    UserResponse,
    UserListResponse,
)
from app.schemas.account_schemas import (
    AccountCreateRequest,
    AccountResponse,
    DepositRequest,
    WithdrawRequest,
    BalanceResponse,
)
from app.schemas.transaction_schemas import (
    TransactionResponse,
    TransactionListResponse,
)

__all__ = [
    "UserCreateRequest",
    "UserResponse",
    "UserListResponse",
    "AccountCreateRequest",
    "AccountResponse",
    "DepositRequest",
    "WithdrawRequest",
    "BalanceResponse",
    "TransactionResponse",
    "TransactionListResponse",
]
