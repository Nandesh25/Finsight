"""
FinSight — User Domain Model

This module defines the User class, which represents a user in the FinSight system.
A User can own multiple Account objects, demonstrating object composition and association.

Key OOP concepts demonstrated:
    - Composition: User "has many" Account objects
    - Association: User manages relationships with Account objects
    - Encapsulation: Accounts are stored privately and accessed through methods
    - Single Responsibility: User manages user-level concerns; Account manages account-level concerns
    - Object collaboration: User delegates account operations to Account objects
"""

from typing import Optional
from enum import Enum

from app.domain.account import Account


class UserRole(Enum):
    """
    Enum for user roles in the system.

    Demonstrates authorization and access control concepts:
        - USER: Standard user with access to their own resources
        - ADMIN: Administrative user with elevated privileges
    """
    USER = "USER"
    ADMIN = "ADMIN"


class User:
    """
    A user in the FinSight system who can own multiple financial accounts.

    This class demonstrates *composition* — a User "has many" Accounts.
    The User object doesn't inherit from Account (that wouldn't make sense);
    instead, it *contains* a collection of Account objects and provides
    methods to manage that collection.

    Key design principles:
        - User manages the collection of accounts
        - User does NOT manipulate Account's internal state (balance)
        - Account operations (deposit/withdraw) remain Account's responsibility
        - User provides convenience methods for finding and organizing accounts

    Attributes:
        user_id: Unique identifier for the user
        name: User's full name
        email: User's email address
        accounts: Read-only property returning the list of accounts (as a copy)
    """

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        hashed_password: Optional[str] = None,
        role: UserRole = UserRole.USER,
    ) -> None:
        """
        Initialize a new User.

        Args:
            user_id: Unique identifier for the user (e.g., "USER-001")
            name: User's full name
            email: User's email address
            hashed_password: Hashed password (never store plain passwords)
            role: User role for authorization (USER or ADMIN)

        Raises:
            ValueError: If user_id, name, or email is empty
        """
        # --- Validation ---
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty.")

        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")

        if not email or not email.strip():
            raise ValueError("Email cannot be empty.")

        # Basic email format validation
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError(f"Invalid email format: {email}")

        # --- Instance Attributes ---
        self.user_id: str = user_id
        self.name: str = name
        self.email: str = email
        self.hashed_password: Optional[str] = hashed_password
        self.role: UserRole = role

        # Private collection of accounts.
        # We use a list because:
        #   - Order might matter (e.g., display accounts in creation order)
        #   - A user can have multiple accounts of the same type
        self._accounts: list[Account] = []

    @property
    def accounts(self) -> list[Account]:
        """
        Return a copy of the user's accounts.

        This property prevents external code from directly modifying
        the internal _accounts list. Callers get a shallow copy, so they
        can iterate or filter without affecting the original collection.

        To add/remove accounts, use add_account() and remove_account().

        Returns:
            A copy of the list of accounts owned by this user.
        """
        return self._accounts.copy()

    def add_account(self, account: Account) -> None:
        """
        Add an account to this user's collection.

        This method demonstrates *composition*. The User doesn't create
        the Account object itself (that's the caller's job); it just
        manages the relationship between User and Account.

        Validation:
            - The account must not be None
            - The account must not already belong to this user

        Args:
            account: The Account object to add

        Raises:
            ValueError: If account is None or already exists for this user
        """
        if account is None:
            raise ValueError("Cannot add None as an account.")

        # Check if this exact account object is already in the collection
        if account in self._accounts:
            raise ValueError(
                f"Account {account.account_number} already belongs to this user."
            )

        # Check for duplicate account_number (different object, same ID)
        if any(acc.account_number == account.account_number for acc in self._accounts):
            raise ValueError(
                f"An account with number {account.account_number} already exists for this user."
            )

        self._accounts.append(account)

    def remove_account(self, account_number: str) -> Account:
        """
        Remove an account from this user's collection by account number.

        This method finds and removes the account, then returns it.
        This allows the caller to inspect or archive the removed account.

        Args:
            account_number: The account number to remove

        Returns:
            The removed Account object

        Raises:
            ValueError: If no account with the given number exists
        """
        for i, account in enumerate(self._accounts):
            if account.account_number == account_number:
                removed_account = self._accounts.pop(i)
                return removed_account

        raise ValueError(
            f"No account found with number '{account_number}' for user {self.user_id}."
        )

    def find_account(self, account_number: str) -> Optional[Account]:
        """
        Find an account by its account number.

        This is a lookup method. It doesn't modify anything; it just
        searches the collection and returns the matching Account (or None).

        Args:
            account_number: The account number to search for

        Returns:
            The Account object if found, None otherwise
        """
        for account in self._accounts:
            if account.account_number == account_number:
                return account
        return None

    def list_accounts(self) -> list[Account]:
        """
        Return a list of all accounts owned by this user.

        This is a convenience method. It's equivalent to accessing the
        `accounts` property, but reads more naturally in some contexts:

            user.list_accounts()  vs.  user.accounts

        Returns:
            A copy of the list of accounts
        """
        return self.accounts

    def get_total_balance(self) -> float:
        """
        Calculate the total balance across all accounts.

        This demonstrates *object collaboration*. The User doesn't reach
        into Account's private _balance attribute. Instead, it calls
        Account's public balance property, respecting encapsulation.

        Returns:
            The sum of balances from all accounts
        """
        return sum(account.balance for account in self._accounts)

    def is_admin(self) -> bool:
        """
        Check if this user has admin privileges.

        This demonstrates role-based authorization.

        Returns:
            True if user has ADMIN role, False otherwise
        """
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the User.

        Returns:
            A string like: User('USER-001', name='John Doe', email='john@example.com', role='USER', accounts=2)
        """
        return (
            f"User('{self.user_id}', "
            f"name='{self.name}', "
            f"email='{self.email}', "
            f"role='{self.role.value}', "
            f"accounts={len(self._accounts)})"
        )
