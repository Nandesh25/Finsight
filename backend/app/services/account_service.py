"""
FinSight — Account Service (Updated with Repository Pattern)

This module defines the AccountService class, which coordinates account-related
business operations using the Repository Pattern for data access.

Key Architecture Concepts:
    - Service Layer: Orchestrates business operations across domain objects
    - Repository Pattern: Uses repositories for data access
    - Dependency Injection: Repositories injected via constructor
    - Separation of Concerns: Services coordinate, repositories handle data access
    - Abstraction: Depends on repository interfaces, not implementations
"""

from typing import Optional
from app.domain.user import User
from app.domain.account import Account
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository


class AccountService:
    """
    Service for account-related operations.

    This service now uses repositories for data access instead of managing
    storage directly. This demonstrates:
        - Dependency Injection: Repositories passed to constructor
        - Separation of Concerns: Service coordinates, repository persists
        - Loose Coupling: Service depends on abstractions (repository interfaces)

    Updated in Phase 7: Now uses repositories for persistence.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        account_repository: AccountRepository,
    ) -> None:
        """
        Initialize the AccountService with repository dependencies.

        This is Dependency Injection in action. The service receives
        its dependencies (repositories) from the outside, rather than
        creating them internally. This enables:
            - Easy testing with mock repositories
            - Swapping implementations without changing the service
            - Clear declaration of dependencies

        Args:
            user_repository: Repository for user data access
            account_repository: Repository for account data access
        """
        self._user_repo = user_repository
        self._account_repo = account_repository
        self._account_counter = 0

    def create_account(
        self,
        user: User,
        account_type: str,
        initial_balance: float = 0.0,
    ) -> Account:
        """
        Create a new account and add it to the user.

        This method now:
        1. Creates the Account domain object
        2. Persists it via repository
        3. Adds it to the User

        Args:
            user: The User who will own the account
            account_type: Type of account ("savings" or "checking")
            initial_balance: Starting balance (default 0.0)

        Returns:
            The newly created Account object

        Raises:
            ValueError: If Account or User validation fails
        """
        # Generate a unique account number
        account_number = self._generate_account_number()

        # Create the Account domain object (validation happens here)
        account = Account(account_number, account_type, balance=initial_balance)

        # Persist the account via repository
        self._account_repo.create(account)

        # Add to user
        user.add_account(account)

        return account

    def deposit(
        self,
        user: User,
        account_number: str,
        amount: float,
    ) -> float:
        """
        Deposit money into an account.

        Now retrieves account from repository instead of from user directly.

        Args:
            user: The User who owns the account
            account_number: The account to deposit into
            amount: Amount to deposit

        Returns:
            The new balance after deposit

        Raises:
            ValueError: If account not found or deposit validation fails
        """
        # Retrieve account from repository
        account = self._account_repo.find_by_account_number(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found."
            )

        # Verify account belongs to user
        if user.find_account(account_number) is None:
            raise ValueError(
                f"Account {account_number} does not belong to user {user.user_id}."
            )

        # Delegate to Account — it handles validation and balance update
        new_balance = account.deposit(amount)

        # Update account in repository
        self._account_repo.update(account)

        return new_balance

    def withdraw(
        self,
        user: User,
        account_number: str,
        amount: float,
    ) -> float:
        """
        Withdraw money from an account.

        Now retrieves and updates account via repository.

        Args:
            user: The User who owns the account
            account_number: The account to withdraw from
            amount: Amount to withdraw

        Returns:
            The new balance after withdrawal

        Raises:
            ValueError: If account not found or withdrawal validation fails
        """
        # Retrieve account from repository
        account = self._account_repo.find_by_account_number(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found."
            )

        # Verify account belongs to user
        if user.find_account(account_number) is None:
            raise ValueError(
                f"Account {account_number} does not belong to user {user.user_id}."
            )

        # Delegate to Account — it handles validation and balance update
        new_balance = account.withdraw(amount)

        # Update account in repository
        self._account_repo.update(account)

        return new_balance

    def get_account_balance(
        self,
        user: User,
        account_number: str,
    ) -> float:
        """
        Get the current balance of an account.

        Args:
            user: The User who owns the account
            account_number: The account to check

        Returns:
            The current account balance

        Raises:
            ValueError: If account not found
        """
        account = self._account_repo.find_by_account_number(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found."
            )

        # Verify account belongs to user
        if user.find_account(account_number) is None:
            raise ValueError(
                f"Account {account_number} does not belong to user {user.user_id}."
            )

        return account.balance

    def get_account(
        self,
        user: User,
        account_number: str,
    ) -> Optional[Account]:
        """
        Retrieve an account by its number.

        Now retrieves from repository instead of from user.

        Args:
            user: The User who owns the account
            account_number: The account to retrieve

        Returns:
            The Account object if found and belongs to user, None otherwise
        """
        account = self._account_repo.find_by_account_number(account_number)

        if account is None:
            return None

        # Verify account belongs to user
        if user.find_account(account_number) is None:
            return None

        return account

    def list_accounts(self, user: User) -> list[Account]:
        """
        List all accounts for a user.

        This still delegates to User.list_accounts since User manages
        the account collection. In a database-backed implementation,
        this might query the repository directly.

        Args:
            user: The User whose accounts to list

        Returns:
            List of Account objects
        """
        return user.list_accounts()

    def close_account(
        self,
        user: User,
        account_number: str,
    ) -> Account:
        """
        Close (remove) an account from a user.

        Now also deletes from repository.

        Args:
            user: The User who owns the account
            account_number: The account to close

        Returns:
            The closed Account object

        Raises:
            ValueError: If account not found or has non-zero balance
        """
        account = self._account_repo.find_by_account_number(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found."
            )

        # Check balance is zero
        if account.balance != 0:
            raise ValueError(
                f"Cannot close account {account_number} with non-zero balance."
            )

        # Remove from user
        removed = user.remove_account(account_number)

        # Delete from repository
        self._account_repo.delete(account_number)

        return removed

    def _generate_account_number(self) -> str:
        """
        Generate a unique account number.

        In a real system with multiple service instances, this would
        use a database sequence or distributed ID generator.

        Returns:
            A unique account number like "ACC-000001"
        """
        self._account_counter += 1
        return f"ACC-{self._account_counter:06d}"
