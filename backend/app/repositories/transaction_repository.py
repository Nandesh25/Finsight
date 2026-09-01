"""
FinSight — Transaction Repository

This module defines the abstract TransactionRepository interface and its in-memory implementation.

The Repository Pattern provides a collection-like interface for accessing Transaction domain objects,
keeping data access logic separate from business logic.

Key Architecture Concepts:
    - Repository Pattern: Collection interface for transactions
    - Abstraction: Contract defined by abstract base class
    - Dependency Injection: Services depend on abstractions
    - Separation of Concerns: Data access isolated from business logic
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.domain.transaction import Transaction, TransactionType


class TransactionRepository(ABC):
    """
    Abstract base class defining the contract for Transaction data access.

    This abstraction enables:
        - Services to work with transactions without knowing storage details
        - Easy swapping between in-memory, database, or other storage
        - Testing with mock repositories
        - Clear separation of concerns

    Design Pattern: Repository Pattern
        Mediates between domain and data layers, providing a collection interface.
    """

    @abstractmethod
    def create(self, transaction: Transaction) -> Transaction:
        """
        Persist a new transaction.

        Args:
            transaction: The Transaction object to persist

        Returns:
            The persisted Transaction object

        Raises:
            ValueError: If a transaction with the same ID already exists
        """
        pass

    @abstractmethod
    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Find a transaction by its ID.

        Args:
            transaction_id: The transaction ID to search for

        Returns:
            The Transaction object if found, None otherwise
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def exists(self, transaction_id: str) -> bool:
        """
        Check if a transaction exists.

        Args:
            transaction_id: The transaction ID to check

        Returns:
            True if transaction exists, False otherwise
        """
        pass

    @abstractmethod
    def list_all(self) -> list[Transaction]:
        """
        Retrieve all transactions.

        Returns:
            List of all Transaction objects
        """
        pass

    @abstractmethod
    def count_by_account(self, account_number: str) -> int:
        """
        Count transactions for an account.

        Args:
            account_number: The account number to count for

        Returns:
            Number of transactions
        """
        pass


class InMemoryTransactionRepository(TransactionRepository):
    """
    In-memory implementation of TransactionRepository.

    Stores transactions in a dictionary keyed by transaction_id for O(1) lookups.
    Uses a secondary index (account_number -> list[transaction_id]) for
    efficient account-based queries.

    This implementation will be replaced with a database-backed version
    in future phases, but services won't need to change because they
    depend on the abstract TransactionRepository interface.

    Thread Safety: NOT thread-safe. Production version needs locking.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory repository.

        Uses two data structures:
        - Primary index: transaction_id -> Transaction (fast lookup by ID)
        - Secondary index: account_number -> list[transaction_id] (fast account queries)
        """
        self._transactions: dict[str, Transaction] = {}
        # Secondary index for finding transactions by account
        self._account_transactions: dict[str, list[str]] = {}

    def create(self, transaction: Transaction) -> Transaction:
        """
        Persist a new transaction.

        Args:
            transaction: The Transaction object to persist

        Returns:
            The persisted Transaction object

        Raises:
            ValueError: If a transaction with the same ID already exists
        """
        if transaction.transaction_id in self._transactions:
            raise ValueError(
                f"Transaction with ID '{transaction.transaction_id}' already exists."
            )

        # Store in primary index
        self._transactions[transaction.transaction_id] = transaction

        # Update secondary index
        if transaction.account_number not in self._account_transactions:
            self._account_transactions[transaction.account_number] = []

        self._account_transactions[transaction.account_number].append(
            transaction.transaction_id
        )

        return transaction

    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Find a transaction by its ID.

        Args:
            transaction_id: The transaction ID to search for

        Returns:
            The Transaction object if found, None otherwise
        """
        return self._transactions.get(transaction_id)

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
        # Get transaction IDs for this account
        transaction_ids = self._account_transactions.get(account_number, [])

        # Get the actual transaction objects
        transactions = [
            self._transactions[txn_id]
            for txn_id in transaction_ids
            if txn_id in self._transactions
        ]

        # Filter by type if specified
        if transaction_type is not None:
            transactions = [
                txn
                for txn in transactions
                if txn.transaction_type == transaction_type
            ]

        # Sort by timestamp, most recent first
        transactions = sorted(
            transactions, key=lambda t: t.timestamp, reverse=True
        )

        # Apply limit if specified
        if limit is not None:
            transactions = transactions[:limit]

        return transactions

    def exists(self, transaction_id: str) -> bool:
        """
        Check if a transaction exists.

        Args:
            transaction_id: The transaction ID to check

        Returns:
            True if transaction exists, False otherwise
        """
        return transaction_id in self._transactions

    def list_all(self) -> list[Transaction]:
        """
        Retrieve all transactions.

        Returns:
            List of all Transaction objects
        """
        return list(self._transactions.values())

    def count_by_account(self, account_number: str) -> int:
        """
        Count transactions for an account.

        Args:
            account_number: The account number to count for

        Returns:
            Number of transactions
        """
        if account_number not in self._account_transactions:
            return 0
        return len(self._account_transactions[account_number])

    def count(self) -> int:
        """
        Count the total number of transactions.

        Helper method for testing and statistics.

        Returns:
            Total number of transactions
        """
        return len(self._transactions)

    def clear(self) -> None:
        """
        Remove all transactions from the repository.

        Helper method for test cleanup.
        """
        self._transactions.clear()
        self._account_transactions.clear()
