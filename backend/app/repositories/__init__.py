"""
Repositories layer.

This module exports repository abstractions and implementations for data access.

Phase 7: In-memory implementations
Phase 8: PostgreSQL implementations added
"""

from .user_repository import UserRepository, InMemoryUserRepository
from .account_repository import AccountRepository, InMemoryAccountRepository
from .transaction_repository import TransactionRepository, InMemoryTransactionRepository
from .postgresql_user_repository import PostgreSQLUserRepository
from .postgresql_account_repository import PostgreSQLAccountRepository
from .postgresql_transaction_repository import PostgreSQLTransactionRepository

__all__ = [
    # Abstractions
    "UserRepository",
    "AccountRepository",
    "TransactionRepository",
    # In-Memory Implementations (Phase 7)
    "InMemoryUserRepository",
    "InMemoryAccountRepository",
    "InMemoryTransactionRepository",
    # PostgreSQL Implementations (Phase 8)
    "PostgreSQLUserRepository",
    "PostgreSQLAccountRepository",
    "PostgreSQLTransactionRepository",
]
