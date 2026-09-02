"""
FinSight — SQLAlchemy Database Models

This module defines the SQLAlchemy ORM models that map to database tables.
These are separate from domain models to maintain separation of concerns.

Key Architecture Concepts:
    - ORM Models: SQLAlchemy classes that map to database tables
    - Separation: Database models are separate from domain models
    - Relationships: Defined using SQLAlchemy relationship()
    - Constraints: Primary keys, foreign keys, and unique constraints
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class AccountTypeEnum(enum.Enum):
    """Enum for account types."""
    SAVINGS = "savings"
    CHECKING = "checking"


class TransactionTypeEnum(enum.Enum):
    """Enum for transaction types."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class UserRoleEnum(enum.Enum):
    """Enum for user roles."""
    USER = "USER"
    ADMIN = "ADMIN"


class UserModel(Base):
    """
    SQLAlchemy model for the users table.

    This is a database model (ORM), separate from the domain model (User).
    The repository layer converts between these two representations.

    Relationships:
        - One user has many accounts (one-to-many)
    """
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=True)  # Nullable for backward compatibility
    role = Column(Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship: User has many Accounts
    accounts = relationship("AccountModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserModel(user_id='{self.user_id}', name='{self.name}', role='{self.role}')>"


class AccountModel(Base):
    """
    SQLAlchemy model for the accounts table.

    This is a database model, separate from the domain model (Account).

    Relationships:
        - Many accounts belong to one user (many-to-one)
        - One account has many transactions (one-to-many)
    """
    __tablename__ = "accounts"

    account_number = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    account_type = Column(Enum(AccountTypeEnum), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="accounts")
    transactions = relationship("TransactionModel", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AccountModel(account_number='{self.account_number}', type='{self.account_type}', balance={self.balance})>"


class TransactionModel(Base):
    """
    SQLAlchemy model for the transactions table.

    This is a database model, separate from the domain model (Transaction).

    Relationships:
        - Many transactions belong to one account (many-to-one)
    """
    __tablename__ = "transactions"

    transaction_id = Column(String(50), primary_key=True)
    account_number = Column(String(50), ForeignKey("accounts.account_number"), nullable=False)
    transaction_type = Column(Enum(TransactionTypeEnum), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    account = relationship("AccountModel", back_populates="transactions")

    def __repr__(self):
        return f"<TransactionModel(transaction_id='{self.transaction_id}', type='{self.transaction_type}', amount={self.amount})>"


class PaymentModel(Base):
    """
    SQLAlchemy model for the payments table.

    This model is prepared for future use but not yet integrated
    into the domain/service layers.
    """
    __tablename__ = "payments"

    payment_id = Column(String(50), primary_key=True)
    from_account = Column(String(50), ForeignKey("accounts.account_number"), nullable=False)
    to_account = Column(String(50), ForeignKey("accounts.account_number"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PaymentModel(payment_id='{self.payment_id}', amount={self.amount}, status='{self.status}')>"
