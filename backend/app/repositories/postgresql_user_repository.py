"""
FinSight — PostgreSQL User Repository

This module implements the UserRepository interface using PostgreSQL and SQLAlchemy.
It demonstrates the Repository Pattern with database persistence.

Key Architecture Concepts:
    - Repository Pattern: Same interface, different implementation
    - ORM Mapping: Converts between domain models and database models
    - Dependency Injection: Session injected via constructor
    - Separation of Concerns: Database details hidden from services
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.domain.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.database.models import UserModel, UserRoleEnum


class PostgreSQLUserRepository(UserRepository):
    """
    PostgreSQL implementation of UserRepository using SQLAlchemy.

    This class implements the same interface as InMemoryUserRepository,
    demonstrating that services don't need to change when we swap
    storage implementations.

    The repository converts between:
        - Domain models (User) - used by services
        - Database models (UserModel) - used by SQLAlchemy

    This separation keeps database concerns out of the domain layer.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy Session for database operations
        """
        self._session = session

    def create(self, user: User) -> User:
        """
        Persist a new user to the database.

        Converts the domain User to a UserModel (ORM), saves it,
        and returns the domain User.

        Args:
            user: The User domain object to persist

        Returns:
            The persisted User object

        Raises:
            ValueError: If a user with the same ID already exists
        """
        # Check if user already exists
        existing = self._session.query(UserModel).filter_by(user_id=user.user_id).first()
        if existing:
            raise ValueError(f"User with ID '{user.user_id}' already exists.")

        # Convert domain model to database model
        db_user = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            hashed_password=user.hashed_password,
            role=UserRoleEnum[user.role.value]
        )

        # Save to database
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)

        # Return the domain model (no conversion needed since input is already domain)
        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Find a user by ID.

        Queries the database and converts the UserModel to a User domain object.

        Args:
            user_id: The user ID to search for

        Returns:
            User domain object if found, None otherwise
        """
        db_user = self._session.query(UserModel).filter_by(user_id=user_id).first()

        if db_user is None:
            return None

        # Convert database model to domain model
        return self._db_user_to_domain(db_user)

    def list_all(self) -> list[User]:
        """
        Retrieve all users from the database.

        Returns:
            List of User domain objects
        """
        db_users = self._session.query(UserModel).all()

        # Convert all database models to domain models
        return [self._db_user_to_domain(db_user) for db_user in db_users]

    def exists(self, user_id: str) -> bool:
        """
        Check if a user exists.

        Args:
            user_id: The user ID to check

        Returns:
            True if user exists, False otherwise
        """
        count = self._session.query(UserModel).filter_by(user_id=user_id).count()
        return count > 0

    def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: The user ID to delete

        Returns:
            True if user was deleted, False if not found
        """
        db_user = self._session.query(UserModel).filter_by(user_id=user_id).first()

        if db_user is None:
            return False

        self._session.delete(db_user)
        self._session.commit()
        return True

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email address.

        This is needed for authentication - users log in with email.

        Args:
            email: The email address to search for

        Returns:
            User domain object if found, None otherwise
        """
        db_user = self._session.query(UserModel).filter_by(email=email).first()

        if db_user is None:
            return None

        # Convert database model to domain model
        return self._db_user_to_domain(db_user)

    def _db_user_to_domain(self, db_user: UserModel) -> User:
        """
        Convert a UserModel (database) to a User (domain).

        This is a private helper method that handles the conversion.
        It keeps the conversion logic centralized and reusable.

        Args:
            db_user: UserModel from database

        Returns:
            User domain object
        """
        # Create domain User object
        user = User(
            user_id=db_user.user_id,
            name=db_user.name,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            role=UserRole[db_user.role.value]
        )

        # Note: We don't load accounts here to avoid unnecessary queries.
        # If accounts are needed, they should be loaded separately.
        # This follows the repository pattern - each repository manages its own entity.

        return user
