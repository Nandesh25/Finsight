"""
FinSight — PostgreSQL Account Repository

This module implements the AccountRepository interface using PostgreSQL and SQLAlchemy.

Key Architecture Concepts:
    - Repository Pattern: Same interface, database implementation
    - ORM Mapping: Converts between Account (domain) and AccountModel (database)
    - Dependency Injection: Session injected via constructor
    - Separation of Concerns: Database details hidden from services
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.domain.account import Account
from app.repositories.account_repository import AccountRepository
from app.database.models import AccountModel, AccountTypeEnum


class PostgreSQLAccountRepository(AccountRepository):
    """
    PostgreSQL implementation of AccountRepository using SQLAlchemy.

    Converts between:
        - Account (domain model) - used by services
        - AccountModel (database model) - used by SQLAlchemy
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy Session for database operations
        """
        self._session = session

    def create(self, account: Account) -> Account:
        """
        Persist a new account to the database.

        Args:
            account: The Account domain object to persist

        Returns:
            The persisted Account object

        Raises:
            ValueError: If an account with the same number already exists
        """
        # Check if account already exists
        existing = self._session.query(AccountModel).filter_by(
            account_number=account.account_number
        ).first()

        if existing:
            raise ValueError(
                f"Account with number '{account.account_number}' already exists."
            )

        # Convert domain model to database model
        db_account = AccountModel(
            account_number=account.account_number,
            user_id="",  # Note: Account domain doesn't have user_id yet
            account_type=AccountTypeEnum[account.account_type.upper()],
            balance=account.balance
        )

        # Save to database
        self._session.add(db_account)
        self._session.commit()
        self._session.refresh(db_account)

        return account

    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        """
        Find an account by its account number.

        Args:
            account_number: The account number to search for

        Returns:
            Account domain object if found, None otherwise
        """
        db_account = self._session.query(AccountModel).filter_by(
            account_number=account_number
        ).first()

        if db_account is None:
            return None

        return self._db_account_to_domain(db_account)

    def find_by_user(self, user_id: str) -> list[Account]:
        """
        Find all accounts belonging to a user.

        Args:
            user_id: The user ID to search for

        Returns:
            List of Account domain objects
        """
        db_accounts = self._session.query(AccountModel).filter_by(
            user_id=user_id
        ).all()

        return [self._db_account_to_domain(db_account) for db_account in db_accounts]

    def update(self, account: Account) -> Account:
        """
        Update an existing account.

        Args:
            account: The Account object with updated state

        Returns:
            The updated Account object

        Raises:
            ValueError: If the account doesn't exist
        """
        db_account = self._session.query(AccountModel).filter_by(
            account_number=account.account_number
        ).first()

        if db_account is None:
            raise ValueError(
                f"Account with number '{account.account_number}' does not exist."
            )

        # Update the database model
        db_account.balance = account.balance
        db_account.account_type = AccountTypeEnum[account.account_type.upper()]

        self._session.commit()
        self._session.refresh(db_account)

        return account

    def exists(self, account_number: str) -> bool:
        """
        Check if an account exists.

        Args:
            account_number: The account number to check

        Returns:
            True if account exists, False otherwise
        """
        count = self._session.query(AccountModel).filter_by(
            account_number=account_number
        ).count()
        return count > 0

    def delete(self, account_number: str) -> bool:
        """
        Delete an account by account number.

        Args:
            account_number: The account number to delete

        Returns:
            True if account was deleted, False if not found
        """
        db_account = self._session.query(AccountModel).filter_by(
            account_number=account_number
        ).first()

        if db_account is None:
            return False

        self._session.delete(db_account)
        self._session.commit()
        return True

    def list_all(self) -> list[Account]:
        """
        Retrieve all accounts.

        Returns:
            List of all Account domain objects
        """
        db_accounts = self._session.query(AccountModel).all()
        return [self._db_account_to_domain(db_account) for db_account in db_accounts]

    def _db_account_to_domain(self, db_account: AccountModel) -> Account:
        """
        Convert an AccountModel (database) to an Account (domain).

        Args:
            db_account: AccountModel from database

        Returns:
            Account domain object
        """
        return Account(
            account_number=db_account.account_number,
            account_type=db_account.account_type.value,
            balance=db_account.balance
        )
