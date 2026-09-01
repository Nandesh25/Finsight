"""
FinSight — PostgreSQL Transaction Repository

This module implements the TransactionRepository interface using PostgreSQL and SQLAlchemy.

Key Architecture Concepts:
    - Repository Pattern: Same interface, database implementation
    - ORM Mapping: Converts between Transaction (domain) and TransactionModel (database)
    - Dependency Injection: Session injected via constructor
    - Separation of Concerns: Database details hidden from services
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.domain.transaction import Transaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.database.models import TransactionModel, TransactionTypeEnum


class PostgreSQLTransactionRepository(TransactionRepository):
    """
    PostgreSQL implementation of TransactionRepository using SQLAlchemy.

    Converts between:
        - Transaction (domain model) - used by services
        - TransactionModel (database model) - used by SQLAlchemy
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy Session for database operations
        """
        self._session = session

    def create(self, transaction: Transaction) -> Transaction:
        """
        Persist a new transaction to the database.

        Args:
            transaction: The Transaction domain object to persist

        Returns:
            The persisted Transaction object

        Raises:
            ValueError: If a transaction with the same ID already exists
        """
        # Check if transaction already exists
        existing = self._session.query(TransactionModel).filter_by(
            transaction_id=transaction.transaction_id
        ).first()

        if existing:
            raise ValueError(
                f"Transaction with ID '{transaction.transaction_id}' already exists."
            )

        # Convert domain model to database model
        db_transaction = TransactionModel(
            transaction_id=transaction.transaction_id,
            account_number=transaction.account_number,
            transaction_type=TransactionTypeEnum[transaction.transaction_type.upper()],
            amount=transaction.amount,
            description=transaction.description,
            timestamp=transaction.timestamp
        )

        # Save to database
        self._session.add(db_transaction)
        self._session.commit()
        self._session.refresh(db_transaction)

        return transaction

    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Find a transaction by its ID.

        Args:
            transaction_id: The transaction ID to search for

        Returns:
            Transaction domain object if found, None otherwise
        """
        db_transaction = self._session.query(TransactionModel).filter_by(
            transaction_id=transaction_id
        ).first()

        if db_transaction is None:
            return None

        return self._db_transaction_to_domain(db_transaction)

    def find_by_account(
        self,
        account_number: str,
        transaction_type: Optional[TransactionType] = None,
        limit: Optional[int] = None,
    ) -> list[Transaction]:
        """
        Find transactions for an account.

        Args:
            account_number: The account number to search for
            transaction_type: Optional filter by type ("deposit" or "withdrawal")
            limit: Optional maximum number of transactions to return

        Returns:
            List of Transaction objects, sorted by timestamp (most recent first)
        """
        # Start with base query
        query = self._session.query(TransactionModel).filter_by(
            account_number=account_number
        )

        # Filter by type if specified
        if transaction_type is not None:
            query = query.filter_by(
                transaction_type=TransactionTypeEnum[transaction_type.upper()]
            )

        # Order by timestamp descending (most recent first)
        query = query.order_by(desc(TransactionModel.timestamp))

        # Apply limit if specified
        if limit is not None:
            query = query.limit(limit)

        # Execute query and convert to domain objects
        db_transactions = query.all()
        return [self._db_transaction_to_domain(t) for t in db_transactions]

    def exists(self, transaction_id: str) -> bool:
        """
        Check if a transaction exists.

        Args:
            transaction_id: The transaction ID to check

        Returns:
            True if transaction exists, False otherwise
        """
        count = self._session.query(TransactionModel).filter_by(
            transaction_id=transaction_id
        ).count()
        return count > 0

    def list_all(self) -> list[Transaction]:
        """
        Retrieve all transactions.

        Returns:
            List of all Transaction domain objects
        """
        db_transactions = self._session.query(TransactionModel).all()
        return [self._db_transaction_to_domain(t) for t in db_transactions]

    def count_by_account(self, account_number: str) -> int:
        """
        Count transactions for an account.

        Args:
            account_number: The account number to count for

        Returns:
            Number of transactions
        """
        return self._session.query(TransactionModel).filter_by(
            account_number=account_number
        ).count()

    def _db_transaction_to_domain(self, db_transaction: TransactionModel) -> Transaction:
        """
        Convert a TransactionModel (database) to a Transaction (domain).

        Args:
            db_transaction: TransactionModel from database

        Returns:
            Transaction domain object
        """
        return Transaction(
            transaction_id=db_transaction.transaction_id,
            account_number=db_transaction.account_number,
            transaction_type=db_transaction.transaction_type.value,
            amount=db_transaction.amount,
            timestamp=db_transaction.timestamp,
            description=db_transaction.description or ""
        )
