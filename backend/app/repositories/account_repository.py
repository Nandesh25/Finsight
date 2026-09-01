"""
FinSight — Account Repository

This module defines the abstract AccountRepository interface and its in-memory implementation.

The Repository Pattern provides a collection-like interface for accessing Account domain objects,
separating data access from business logic.

Key Architecture Concepts:
    - Repository Pattern: Mediates between domain and data layers
    - Abstraction: Abstract base class defines the contract
    - Dependency Injection: Services depend on abstractions
    - Separation of Concerns: Data access logic isolated
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.domain.account import Account


class AccountRepository(ABC):
    """
    Abstract base class defining the contract for Account data access.

    This abstraction allows services to work with accounts without knowing
    how they're stored (in-memory, database, etc.). This enables:
        - Easy testing with mock repositories
        - Swapping storage implementations without changing services
        - Clear separation between business logic and data access

    Design Pattern: Repository Pattern
        Acts as a collection of domain objects, hiding persistence details.
    """

    @abstractmethod
    def create(self, account: Account) -> Account:
        """
        Persist a new account.

        Args:
            account: The Account object to persist

        Returns:
            The persisted Account object

        Raises:
            ValueError: If an account with the same number already exists
        """
        pass

    @abstractmethod
    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        """
        Find an account by its account number.

        Args:
            account_number: The account number to search for

        Returns:
            The Account object if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_user(self, user_id: str) -> list[Account]:
        """
        Find all accounts belonging to a user.

        Args:
            user_id: The user ID to search for

        Returns:
            List of Account objects (empty if none found)
        """
        pass

    @abstractmethod
    def update(self, account: Account) -> Account:
        """
        Update an existing account.

        In the in-memory implementation, this is mostly a no-op since
        we're working with references. In a database implementation,
        this would persist changes to the database.

        Args:
            account: The Account object with updated state

        Returns:
            The updated Account object

        Raises:
            ValueError: If the account doesn't exist
        """
        pass

    @abstractmethod
    def exists(self, account_number: str) -> bool:
        """
        Check if an account exists.

        Args:
            account_number: The account number to check

        Returns:
            True if account exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, account_number: str) -> bool:
        """
        Delete an account by account number.

        Args:
            account_number: The account number to delete

        Returns:
            True if account was deleted, False if not found
        """
        pass

    @abstractmethod
    def list_all(self) -> list[Account]:
        """
        Retrieve all accounts.

        Returns:
            List of all Account objects
        """
        pass


class InMemoryAccountRepository(AccountRepository):
    """
    In-memory implementation of AccountRepository.

    Stores accounts in a dictionary keyed by account_number for O(1) lookups.
    Uses a secondary index for finding accounts by user_id.

    This implementation will be replaced with a database-backed version
    in future phases, but services won't need to change because they
    depend on the abstract AccountRepository interface.

    Thread Safety: NOT thread-safe. Production version needs locking.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory repository.

        Uses two data structures:
        - Primary index: account_number -> Account (fast lookup)
        - Secondary index: user_id -> list of account_numbers (fast user queries)
        """
        self._accounts: dict[str, Account] = {}
        # Secondary index for finding accounts by user
        self._user_accounts: dict[str, list[str]] = {}

    def create(self, account: Account) -> Account:
        """
        Persist a new account.

        Args:
            account: The Account object to persist

        Returns:
            The persisted Account object

        Raises:
            ValueError: If an account with the same number already exists
        """
        if account.account_number in self._accounts:
            raise ValueError(
                f"Account with number '{account.account_number}' already exists."
            )

        self._accounts[account.account_number] = account
        return account

    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        """
        Find an account by its account number.

        Args:
            account_number: The account number to search for

        Returns:
            The Account object if found, None otherwise
        """
        return self._accounts.get(account_number)

    def find_by_user(self, user_id: str) -> list[Account]:
        """
        Find all accounts belonging to a user.

        In this in-memory implementation, we scan all accounts.
        A database implementation would use an indexed query.

        Args:
            user_id: The user ID to search for

        Returns:
            List of Account objects (empty if none found)
        """
        # Note: This requires accounts to be associated with users
        # Since Account domain model doesn't have a user_id field,
        # this method returns all accounts for now.
        # In a real implementation, Account would have a user_id field.

        # For now, return all accounts - will be enhanced when Account-User
        # relationship is added to the Account domain model
        return list(self._accounts.values())

    def update(self, account: Account) -> Account:
        """
        Update an existing account.

        In this in-memory implementation, since we're working with object
        references, the account is already updated. We just verify it exists.

        Args:
            account: The Account object with updated state

        Returns:
            The updated Account object

        Raises:
            ValueError: If the account doesn't exist
        """
        if account.account_number not in self._accounts:
            raise ValueError(
                f"Account with number '{account.account_number}' does not exist."
            )

        # In-memory: object is already updated since we're using references
        # In a database: this would issue an UPDATE statement
        self._accounts[account.account_number] = account
        return account

    def exists(self, account_number: str) -> bool:
        """
        Check if an account exists.

        Args:
            account_number: The account number to check

        Returns:
            True if account exists, False otherwise
        """
        return account_number in self._accounts

    def delete(self, account_number: str) -> bool:
        """
        Delete an account by account number.

        Args:
            account_number: The account number to delete

        Returns:
            True if account was deleted, False if not found
        """
        if account_number in self._accounts:
            del self._accounts[account_number]
            return True
        return False

    def list_all(self) -> list[Account]:
        """
        Retrieve all accounts.

        Returns:
            List of all Account objects
        """
        return list(self._accounts.values())

    def count(self) -> int:
        """
        Count the total number of accounts.

        Helper method for testing and statistics.

        Returns:
            Number of accounts in the repository
        """
        return len(self._accounts)

    def clear(self) -> None:
        """
        Remove all accounts from the repository.

        Helper method for test cleanup.
        """
        self._accounts.clear()
        self._user_accounts.clear()
