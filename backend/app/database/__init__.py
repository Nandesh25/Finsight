"""
Database layer.

This module exports database configuration and models for PostgreSQL persistence.
"""

from .config import (
    engine,
    SessionLocal,
    init_database,
    drop_database,
    get_db_session,
    get_db_session_for_testing,
    DatabaseConfig,
)
from .models import (
    Base,
    UserModel,
    AccountModel,
    TransactionModel,
    PaymentModel,
    AccountTypeEnum,
    TransactionTypeEnum,
)

__all__ = [
    # Configuration
    "engine",
    "SessionLocal",
    "init_database",
    "drop_database",
    "get_db_session",
    "get_db_session_for_testing",
    "DatabaseConfig",
    # Models
    "Base",
    "UserModel",
    "AccountModel",
    "TransactionModel",
    "PaymentModel",
    "AccountTypeEnum",
    "TransactionTypeEnum",
]
