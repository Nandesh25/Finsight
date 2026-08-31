"""
FinSight — Account Domain Model

This module defines the Account class, the first domain model in FinSight.
It represents a financial account with basic banking operations.

Key OOP concepts demonstrated:
    - Class definition and instantiation
    - __init__ (constructor) for initializing object state
    - Instance attributes to store per-object data
    - Instance methods to define object behavior
    - Type hints for code clarity and tooling support
    - Encapsulation via @property: private state with controlled access
    - Exception handling with ValueError for validation
"""


class Account:
    """
    A financial account with deposit and withdrawal capabilities.

    This class models a simple bank account. Each Account object holds
    its own account_number, account_type, and balance — these are
    *instance attributes*, meaning every Account you create has its
    own independent copy of these values.

    Encapsulation:
        The balance is stored in a *private* attribute ``_balance`` and
        exposed through a read-only ``@property``.  This means:

        - Reading:  ``account.balance``      → works (returns the value)
        - Writing:  ``account.balance = 999`` → raises AttributeError

        The only way to change the balance is through ``deposit()`` and
        ``withdraw()``, which enforce validation rules.

    Attributes:
        account_number: A unique identifier for the account (e.g., "ACC-001").
        account_type: The type of account — "savings" or "checking".
        balance: The current monetary balance (read-only property).
    """

    # These are the only account types we allow.
    VALID_ACCOUNT_TYPES = ("savings", "checking")

    def __init__(
        self,
        account_number: str,
        account_type: str,
        balance: float = 0.0,
    ) -> None:
        """
        Initialize a new Account.

        __init__ is Python's constructor — it runs automatically when you
        create an Account object with Account("ACC-001", "savings").
        Its job is to set up the initial state of the object.

        The 'self' parameter refers to the specific object being created.
        Think of it as "this account" — self._balance means "this account's
        balance".

        Args:
            account_number: Unique identifier for the account.
            account_type: Must be "savings" or "checking".
            balance: Starting balance (defaults to 0.0, cannot be negative).

        Raises:
            ValueError: If account_number is empty, account_type is invalid,
                        or balance is negative.
        """
        # --- Validation ---
        # We validate inputs in __init__ so that it's impossible to create
        # an Account in an invalid state. This is a core OOP idea:
        # the object protects its own data integrity.

        if not account_number or not account_number.strip():
            raise ValueError("Account number cannot be empty.")

        if account_type not in self.VALID_ACCOUNT_TYPES:
            raise ValueError(
                f"Invalid account type '{account_type}'. "
                f"Must be one of: {self.VALID_ACCOUNT_TYPES}"
            )

        if balance < 0:
            raise ValueError(
                f"Initial balance cannot be negative (got {balance})."
            )

        # --- Instance Attributes ---
        # account_number and account_type are public — reading them is fine.
        # _balance is private (prefixed with _) — it should only be modified
        # by methods inside this class. The @property below provides
        # read-only access from outside.
        self.account_number: str = account_number
        self.account_type: str = account_type
        self._balance: float = balance

    # ──────────────────────────────────────────────
    #  Property: balance (read-only)
    # ──────────────────────────────────────────────

    @property
    def balance(self) -> float:
        """
        The current account balance (read-only).

        @property turns this method into an attribute-like accessor.
        External code can read it with ``account.balance``, but cannot
        set it with ``account.balance = 999`` — that raises AttributeError.

        WHY a property instead of a plain attribute?
            Before (Phase 2):  self.balance was public — anyone could write
                               account.balance = -9999 and break the rules.
            Now:               self._balance is private.  The @property
                               exposes it for reading only.  All writes go
                               through deposit() / withdraw(), which validate.

        Returns:
            The current account balance.
        """
        return self._balance

    def deposit(self, amount: float) -> float:
        """
        Deposit money into the account.

        This is an *instance method* — it operates on a specific Account
        object (via self). It reads and modifies self._balance, which is
        this account's balance.

        Args:
            amount: The amount to deposit (must be positive).

        Returns:
            The new balance after the deposit.

        Raises:
            ValueError: If amount is not positive.
        """
        if amount <= 0:
            raise ValueError(
                f"Deposit amount must be positive (got {amount})."
            )

        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> float:
        """
        Withdraw money from the account.

        Before allowing the withdrawal, this method checks two things:
            1. The amount must be positive (you can't withdraw $0 or -$50).
            2. The account must have enough funds (no overdrafts).

        This is *encapsulation* in action — external code cannot bypass
        these rules because _balance is private. The only way to change
        the balance is through this method (or deposit), both of which
        enforce validation.

        Args:
            amount: The amount to withdraw (must be positive).

        Returns:
            The new balance after the withdrawal.

        Raises:
            ValueError: If amount is not positive or exceeds the balance.
        """
        if amount <= 0:
            raise ValueError(
                f"Withdrawal amount must be positive (got {amount})."
            )

        if amount > self._balance:
            raise ValueError(
                f"Insufficient balance. "
                f"Tried to withdraw {amount}, but balance is {self._balance}."
            )

        self._balance -= amount
        return self._balance

    def get_balance(self) -> float:
        """
        Return the current balance.

        This method is kept for backward compatibility. With the @property
        in place, you can also use ``account.balance`` directly.

        Returns:
            The current account balance.
        """
        return self._balance

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the Account.

        __repr__ is a special "dunder" (double-underscore) method. Python
        calls it when you print an object or inspect it in the REPL.
        Without it, printing an Account would show something unhelpful
        like <app.domain.account.account.Account object at 0x...>.

        Returns:
            A string like: Account('ACC-001', type='savings', balance=500.0)
        """
        return (
            f"Account('{self.account_number}', "
            f"type='{self.account_type}', "
            f"balance={self._balance})"
        )
