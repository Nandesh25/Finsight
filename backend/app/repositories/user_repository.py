"""
FinSight — User Repository

This module defines the abstract UserRepository interface and its in-memory implementation.

The Repository Pattern separates data access logic from business logic, providing
a collection-like interface for accessing domain objects.

Key Architecture Concepts:
    - Repository Pattern: Collection-like interface for domain objects
    - Abstraction: Abstract base class defines the contract
    - Dependency Injection: Services depend on the abstraction, not the implementation
    - Separation of Concerns: Data access separated from business logic
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.domain.user import User


class UserRepository(ABC):
    """
    Abstract base class defining the contract for User data access.

    This is an abstraction (interface) that defines what operations
    are available for User persistence without specifying how they're
    implemented. This allows:
        - Services to depend on the abstraction, not concrete implementations
        - Easy swapping between in-memory, database, or other storage
        - Testing with mock repositories

    Design Pattern: Repository Pattern
        Provides a collection-like interface for accessing domain objects.
        The repository acts as a mediator between the domain and data layers.
    """

    @abstractmethod
    def create(self, user: User) -> User:
        """
        Persist a new user.

        Args:
            user: The User object to persist

        Returns:
            The persisted User object

        Raises:
            ValueError: If a user with the same ID already exists
        """
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Find a user by their ID.

        Args:
            user_id: The user ID to search for

        Returns:
            The User object if found, None otherwise
        """
        pass

    @abstractmethod
    def list_all(self) -> list[User]:
        """
        Retrieve all users.

        Returns:
            List of all User objects
        """
        pass

    @abstractmethod
    def exists(self, user_id: str) -> bool:
        """
        Check if a user exists.

        Args:
            user_id: The user ID to check

        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: The user ID to delete

        Returns:
            True if user was deleted, False if not found
        """
        pass


class InMemoryUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository.

    This stores users in a dictionary for fast lookup. In future phases,
    this will be replaced with a database-backed implementation, but
    the services won't need to change because they depend on the
    abstract UserRepository interface.

    Thread Safety: This implementation is NOT thread-safe. A production
    version would need locking or use a thread-safe data structure.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory repository.

        Uses a dictionary for O(1) lookups by user_id.
        """
        self._users: dict[str, User] = {}

    def create(self, user: User) -> User:
        """
        Persist a new user.

        Args:
            user: The User object to persist

        Returns:
            The persisted User object

        Raises:
            ValueError: If a user with the same ID already exists
        """
        if user.user_id in self._users:
            raise ValueError(f"User with ID '{user.user_id}' already exists.")

        self._users[user.user_id] = user
        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Find a user by their ID.

        Args:
            user_id: The user ID to search for

        Returns:
            The User object if found, None otherwise
        """
        return self._users.get(user_id)

    def list_all(self) -> list[User]:
        """
        Retrieve all users.

        Returns:
            List of all User objects
        """
        return list(self._users.values())

    def exists(self, user_id: str) -> bool:
        """
        Check if a user exists.

        Args:
            user_id: The user ID to check

        Returns:
            True if user exists, False otherwise
        """
        return user_id in self._users

    def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: The user ID to delete

        Returns:
            True if user was deleted, False if not found
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def count(self) -> int:
        """
        Count the total number of users.

        This is a helper method not in the abstract interface.
        Useful for testing and statistics.

        Returns:
            Number of users in the repository
        """
        return len(self._users)

    def clear(self) -> None:
        """
        Remove all users from the repository.

        This is a helper method not in the abstract interface.
        Useful for test cleanup.
        """
        self._users.clear()
