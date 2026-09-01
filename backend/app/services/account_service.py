"""
FinSight — Account Service

This module defines the AccountService class, which coordinates account-related
business operations. This is the service layer that sits between the API/UI
and the domain models.

Key Architecture Concepts:
    - Service Layer: Orchestrates business operations across domain objects
    - Separation of Concerns: Services coordinate, domains contain business logic
    - Dependency Injection: Services depend on abstractions, not concrete implementations
    - Single Responsibility: AccountService handles account operations only
"""

from typing import Optional
from app.domain.user import User
from app.domain.account import Account
from app.domain.transaction import Transaction
from datetime import datetime


class AccountService:
    """
    Service for account-related operations.

    This service coordinates operations between User and Account domain objects.
    It does NOT duplicate the business logic that already exists in Account
    (validation, balance management) — it delegates to those objects.

    Responsibility:
        - Coordinate User and Account objects
        - Generate unique IDs for accounts
        - Provide a convenient API for account operations
        - Handle cross-object operations (e.g., creating account and adding to user)

    What it does NOT do:
        - Duplicate Account's validation logic
        - Directly manipulate Account's internal state
        - Replace domain object behavior

    Design Pattern: Service Layer
        The service layer sits between the presentation layer (API/UI) and
        the domain layer. It orchestrates use cases without containing
        business rules (those live in the domain).
    """

    def __init__(self) -> None:
        """
        Initialize the AccountService.

        In future phases, this is where we'll inject dependencies like
        repositories, event publishers, etc. For now, it's stateless.
        """
        self._account_counter = 0

    def create_account(
        self,
        user: User,
        account_type: str,
        initial_balance: float = 0.0,
    ) -> Account:
        """
        Create a new account and add it to the user.

        This method coordinates two operations:
        1. Create the Account domain object
        2. Add it to the User

        The business rules (valid account types, non-negative balance) are
        enforced by the Account class itself, not by this service.

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

        # Create the Account domain object
        # Validation happens inside Account.__init__
        account = Account(account_number, account_type, balance=initial_balance)

        # Add to user
        # Validation happens inside User.add_account
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

        This service method:
        1. Finds the account in the user's collection
        2. Delegates the deposit operation to the Account object

        The deposit validation (positive amount) is handled by Account,
        not by this service.

        Args:
            user: The User who owns the account
            account_number: The account to deposit into
            amount: Amount to deposit

        Returns:
            The new balance after deposit

        Raises:
            ValueError: If account not found or deposit validation fails
        """
        account = user.find_account(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found for user {user.user_id}."
            )

        # Delegate to Account — it handles validation and balance update
        new_balance = account.deposit(amount)
        return new_balance

    def withdraw(
        self,
        user: User,
        account_number: str,
        amount: float,
    ) -> float:
        """
        Withdraw money from an account.

        This service method:
        1. Finds the account in the user's collection
        2. Delegates the withdrawal operation to the Account object

        The withdrawal validation (positive amount, sufficient balance) is
        handled by Account, not by this service.

        Args:
            user: The User who owns the account
            account_number: The account to withdraw from
            amount: Amount to withdraw

        Returns:
            The new balance after withdrawal

        Raises:
            ValueError: If account not found or withdrawal validation fails
        """
        account = user.find_account(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found for user {user.user_id}."
            )

        # Delegate to Account — it handles validation and balance update
        new_balance = account.withdraw(amount)
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
        account = user.find_account(account_number)

        if account is None:
            raise ValueError(
                f"Account {account_number} not found for user {user.user_id}."
            )

        return account.balance

    def get_account(
        self,
        user: User,
        account_number: str,
    ) -> Optional[Account]:
        """
        Retrieve an account by its number.

        This is a convenience method that delegates to User.find_account.

        Args:
            user: The User who owns the account
            account_number: The account to retrieve

        Returns:
            The Account object if found, None otherwise
        """
        return user.find_account(account_number)

    def list_accounts(self, user: User) -> list[Account]:
        """
        List all accounts for a user.

        This is a convenience method that delegates to User.list_accounts.

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

        This delegates to User.remove_account. In a real system, you might
        add additional checks here (e.g., balance must be zero, no pending
        transactions, etc.).

        Args:
            user: The User who owns the account
            account_number: The account to close

        Returns:
            The closed Account object

        Raises:
            ValueError: If account not found
        """
        # Future enhancement: check balance is zero
        account = user.find_account(account_number)
        if account and account.balance != 0:
            raise ValueError(
                f"Cannot close account {account_number} with non-zero balance."
            )

        return user.remove_account(account_number)

    def _generate_account_number(self) -> str:
        """
        Generate a unique account number.

        In a real system, this would use a database sequence, UUID, or
        distributed ID generator. For this in-memory implementation, we
        use a simple counter.

        Returns:
            A unique account number like "ACC-000001"
        """
        self._account_counter += 1
        return f"ACC-{self._account_counter:06d}"
