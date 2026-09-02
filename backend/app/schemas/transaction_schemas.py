"""
FinSight — Transaction API Schemas

Pydantic models for transaction-related API requests and responses.

Key Architecture Concepts:
    - Read-Only Resources: Transactions are immutable once created
    - Query Parameters: Filter options for listing transactions
    - Timestamping: ISO 8601 format for consistent date/time representation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class TransactionResponse(BaseModel):
    """
    Response schema for a single transaction.

    Transactions are read-only once created, so there's no
    TransactionCreateRequest — transactions are created through
    deposit/withdraw operations on accounts.
    """
    transaction_id: str
    account_number: str
    transaction_type: Literal["deposit", "withdrawal"]
    amount: float
    description: str
    timestamp: str  # ISO 8601 format

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-000001",
                "account_number": "ACC-000001",
                "transaction_type": "deposit",
                "amount": 500.0,
                "description": "Salary deposit",
                "timestamp": "2026-09-02T15:42:45.468Z"
            }
        }


class TransactionListResponse(BaseModel):
    """
    Response schema for listing transactions.

    Returns a list of transactions with metadata.
    """
    transactions: List[TransactionResponse]
    count: int
    account_number: str

    class Config:
        json_schema_extra = {
            "example": {
                "transactions": [
                    {
                        "transaction_id": "TXN-000001",
                        "account_number": "ACC-000001",
                        "transaction_type": "deposit",
                        "amount": 500.0,
                        "description": "Salary deposit",
                        "timestamp": "2026-09-02T15:42:45.468Z"
                    }
                ],
                "count": 1,
                "account_number": "ACC-000001"
            }
        }
