"""
FinSight — Transaction Domain Model

This module defines the Transaction class, which represents a financial transaction
(deposit or withdrawal) on an Account. Transactions are immutable records once created.

Key OOP concepts demonstrated:
    - Immutability: Transaction state cannot be changed after creation
    - Value Object: Transaction represents a record of an operation
    - Encapsulation: All attributes are read-only
    - Type hints for clarity
    - Validation at creation time
"""

from datetime import datetime
from typing import Literal


# Type alias for transaction types
TransactionType = Literal["deposit", "withdrawal"]


class Transaction:
    """
    An immutable record of a financial transaction.

    Once a Transaction is created, its properties cannot be changed.
    This makes Transactions ideal for audit trails and historical records.

    Design Pattern: Value Object
        Transactions are value objects — they're identified by their attributes,
        not by an identity. Two transactions with the same values are considered
        equal for comparison purposes.

    Immutability:
        All attributes are read-only (no setters). The only way to "change" a
        transaction is to create a new one. This ensures data integrity and
        makes the system easier to reason about.

    Attributes:
        transaction_id: Unique identifier for this transaction
        account_number: The account this transaction belongs to
        transaction_type: Either "deposit" or "withdrawal"
        amount: The monetary amount (always positive)
        timestamp: When the transaction occurred
        description: Optional description of the transaction
    """

    VALID_TRANSACTION_TYPES = ("deposit", "withdrawal")

    def __init__(
        self,
        transaction_id: str,
        account_number: str,
        transaction_type: TransactionType,
        amount: float,
        timestamp: datetime | None = None,
        description: str = "",
    ) -> None:
        """
        Initialize a new Transaction.

        Transactions are immutable once created. All validation happens here.

        Args:
            transaction_id: Unique identifier (e.g., "TXN-001")
            account_number: The account this transaction belongs to
            transaction_type: Either "deposit" or "withdrawal"
            amount: Transaction amount (must be positive)
            timestamp: When the transaction occurred (defaults to now)
            description: Optional description

        Raises:
            ValueError: If validation fails
        """
        # --- Validation ---
        if not transaction_id or not transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty.")

        if not account_number or not account_number.strip():
            raise ValueError("Account number cannot be empty.")

        if transaction_type not in self.VALID_TRANSACTION_TYPES:
            raise ValueError(
                f"Invalid transaction type '{transaction_type}'. "
                f"Must be one of: {self.VALID_TRANSACTION_TYPES}"
            )

        if amount <= 0:
            raise ValueError(
                f"Transaction amount must be positive (got {amount})."
            )

        # --- Instance Attributes ---
        # All attributes are public but effectively read-only because
        # there are no setter methods. This is immutability through convention.
        self._transaction_id: str = transaction_id
        self._account_number: str = account_number
        self._transaction_type: TransactionType = transaction_type
        self._amount: float = amount
        self._timestamp: datetime = timestamp if timestamp else datetime.now()
        self._description: str = description.strip()

    # ──────────────────────────────────────────────
    #  Read-only Properties
    # ──────────────────────────────────────────────

    @property
    def transaction_id(self) -> str:
        """The unique transaction identifier (read-only)."""
        return self._transaction_id

    @property
    def account_number(self) -> str:
        """The account number this transaction belongs to (read-only)."""
        return self._account_number

    @property
    def transaction_type(self) -> TransactionType:
        """The type of transaction: 'deposit' or 'withdrawal' (read-only)."""
        return self._transaction_type

    @property
    def amount(self) -> float:
        """The transaction amount (read-only)."""
        return self._amount

    @property
    def timestamp(self) -> datetime:
        """When the transaction occurred (read-only)."""
        return self._timestamp

    @property
    def description(self) -> str:
        """Optional transaction description (read-only)."""
        return self._description

    def is_deposit(self) -> bool:
        """
        Check if this is a deposit transaction.

        Returns:
            True if transaction_type is "deposit"
        """
        return self._transaction_type == "deposit"

    def is_withdrawal(self) -> bool:
        """
        Check if this is a withdrawal transaction.

        Returns:
            True if transaction_type is "withdrawal"
        """
        return self._transaction_type == "withdrawal"

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation.

        Returns:
            String like: Transaction('TXN-001', type='deposit', amount=100.0)
        """
        return (
            f"Transaction('{self._transaction_id}', "
            f"account='{self._account_number}', "
            f"type='{self._transaction_type}', "
            f"amount={self._amount})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Compare two transactions for equality.

        Two transactions are equal if all their attributes match.
        This is value object behavior — compared by value, not identity.

        Args:
            other: Another object to compare

        Returns:
            True if all attributes match
        """
        if not isinstance(other, Transaction):
            return False

        return (
            self._transaction_id == other._transaction_id
            and self._account_number == other._account_number
            and self._transaction_type == other._transaction_type
            and self._amount == other._amount
            and self._timestamp == other._timestamp
            and self._description == other._description
        )

    def __hash__(self) -> int:
        """
        Generate a hash for this transaction.

        This allows Transactions to be used in sets and as dict keys.
        Since Transactions are immutable, their hash won't change.

        Returns:
            Integer hash value
        """
        return hash(
            (
                self._transaction_id,
                self._account_number,
                self._transaction_type,
                self._amount,
                self._timestamp,
                self._description,
            )
        )
