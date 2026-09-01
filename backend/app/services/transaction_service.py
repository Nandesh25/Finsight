"""
FinSight — Transaction Service

This module defines the TransactionService class, which coordinates transaction-related
business operations. This service manages the creation and retrieval of transaction
records for accounts.

Key Architecture Concepts:
    - Service Layer: Orchestrates transaction operations
    - Separation of Concerns: Service coordinates, domains enforce rules
    - Dependency Injection: Designed for future repository injection
    - Single Responsibility: TransactionService handles transactions only
"""

from typing import Optional
from datetime import datetime
from app.domain.user import User
from app.domain.account import Account
from app.domain.transaction import Transaction, TransactionType


class TransactionService:
    """
    Service for transaction-related operations.

    This service coordinates transaction creation, validation, and retrieval.
    It works with Account objects to ensure transactions are properly recorded
    and validated.

    Responsibility:
        - Create transaction records for deposits/withdrawals
        - Generate unique transaction IDs
        - Retrieve transaction history for accounts
        - Validate transactions before creation

    Design Pattern: Service Layer
        Coordinates use cases involving transactions. In future phases,
        this will interact with a TransactionRepository for persistence.
    """

    def __init__(self) -> None:
        """
        Initialize the TransactionService.

        For now, we store transactions in memory. In future phases, this
        will be replaced with a repository pattern for database persistence.
        """
        self._transaction_counter = 0
        # In-memory storage: account_number -> list of transactions
        self._transactions: dict[str, list[Transaction]] = {}

    def create_transaction(
        self,
        account: Account,
        transaction_type: TransactionType,
        amount: float,
        description: str = "",
    ) -> Transaction:
        """
        Create a transaction record for an account operation.

        This method creates an immutable Transaction object to record a
        deposit or withdrawal. It does NOT modify the account balance —
        that should be done separately through Account.deposit/withdraw.

        This separation allows for:
        - Atomic operations (update balance + record transaction)
        - Transaction history tracking
        - Audit trails

        Args:
            account: The Account this transaction belongs to
            transaction_type: Either "deposit" or "withdrawal"
            amount: Transaction amount (must be positive)
            description: Optional description

        Returns:
            The created Transaction object

        Raises:
            ValueError: If validation fails
        """
        # Generate unique transaction ID
        transaction_id = self._generate_transaction_id()

        # Create the Transaction domain object
        # Validation happens inside Transaction.__init__
        transaction = Transaction(
            transaction_id=transaction_id,
            account_number=account.account_number,
            transaction_type=transaction_type,
            amount=amount,
            timestamp=datetime.now(),
            description=description,
        )

        # Store in our in-memory registry
        if account.account_number not in self._transactions:
            self._transactions[account.account_number] = []

        self._transactions[account.account_number].append(transaction)

        return transaction

    def validate_transaction(
        self,
        account: Account,
        transaction_type: TransactionType,
        amount: float,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate whether a transaction can be performed.

        This checks if the transaction would be valid without actually
        executing it. Useful for pre-flight checks in the UI.

        Args:
            account: The Account to validate against
            transaction_type: Either "deposit" or "withdrawal"
            amount: Transaction amount

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, "error message") if invalid
        """
        # Check amount is positive
        if amount <= 0:
            return False, f"Transaction amount must be positive (got {amount})."

        # Check withdrawal has sufficient balance
        if transaction_type == "withdrawal":
            if amount > account.balance:
                return False, f"Insufficient balance. Tried to withdraw {amount}, but balance is {account.balance}."

        return True, None

    def get_transactions(
        self,
        account_number: str,
        transaction_type: Optional[TransactionType] = None,
        limit: Optional[int] = None,
    ) -> list[Transaction]:
        """
        Retrieve transactions for an account.

        Args:
            account_number: The account to retrieve transactions for
            transaction_type: Filter by type ("deposit" or "withdrawal"), None for all
            limit: Maximum number of transactions to return, None for all

        Returns:
            List of Transaction objects, most recent first
        """
        if account_number not in self._transactions:
            return []

        transactions = self._transactions[account_number]

        # Filter by type if specified
        if transaction_type is not None:
            transactions = [
                txn for txn in transactions
                if txn.transaction_type == transaction_type
            ]

        # Sort by timestamp, most recent first
        transactions = sorted(transactions, key=lambda t: t.timestamp, reverse=True)

        # Apply limit if specified
        if limit is not None:
            transactions = transactions[:limit]

        return transactions

    def get_transaction_by_id(
        self,
        transaction_id: str,
    ) -> Optional[Transaction]:
        """
        Retrieve a specific transaction by its ID.

        Args:
            transaction_id: The transaction ID to search for

        Returns:
            The Transaction object if found, None otherwise
        """
        for transactions in self._transactions.values():
            for txn in transactions:
                if txn.transaction_id == transaction_id:
                    return txn
        return None

    def get_transaction_count(self, account_number: str) -> int:
        """
        Get the total number of transactions for an account.

        Args:
            account_number: The account to count transactions for

        Returns:
            Number of transactions
        """
        if account_number not in self._transactions:
            return 0
        return len(self._transactions[account_number])

    def get_total_deposited(self, account_number: str) -> float:
        """
        Calculate total amount deposited to an account.

        Args:
            account_number: The account to calculate for

        Returns:
            Total deposit amount
        """
        transactions = self.get_transactions(account_number, transaction_type="deposit")
        return sum(txn.amount for txn in transactions)

    def get_total_withdrawn(self, account_number: str) -> float:
        """
        Calculate total amount withdrawn from an account.

        Args:
            account_number: The account to calculate for

        Returns:
            Total withdrawal amount
        """
        transactions = self.get_transactions(account_number, transaction_type="withdrawal")
        return sum(txn.amount for txn in transactions)

    def record_deposit(
        self,
        account: Account,
        amount: float,
        description: str = "",
    ) -> tuple[Transaction, float]:
        """
        Record a deposit transaction and update the account balance.

        This is a convenience method that combines:
        1. Executing the deposit on the account
        2. Creating a transaction record

        This ensures the transaction record and balance change are consistent.

        Args:
            account: The Account to deposit to
            amount: Amount to deposit
            description: Optional description

        Returns:
            Tuple of (Transaction, new_balance)

        Raises:
            ValueError: If deposit validation fails
        """
        # Execute the deposit (Account validates and updates balance)
        new_balance = account.deposit(amount)

        # Create the transaction record
        transaction = self.create_transaction(
            account=account,
            transaction_type="deposit",
            amount=amount,
            description=description,
        )

        return transaction, new_balance

    def record_withdrawal(
        self,
        account: Account,
        amount: float,
        description: str = "",
    ) -> tuple[Transaction, float]:
        """
        Record a withdrawal transaction and update the account balance.

        This is a convenience method that combines:
        1. Executing the withdrawal on the account
        2. Creating a transaction record

        This ensures the transaction record and balance change are consistent.

        Args:
            account: The Account to withdraw from
            amount: Amount to withdraw
            description: Optional description

        Returns:
            Tuple of (Transaction, new_balance)

        Raises:
            ValueError: If withdrawal validation fails
        """
        # Execute the withdrawal (Account validates and updates balance)
        new_balance = account.withdraw(amount)

        # Create the transaction record
        transaction = self.create_transaction(
            account=account,
            transaction_type="withdrawal",
            amount=amount,
            description=description,
        )

        return transaction, new_balance

    def _generate_transaction_id(self) -> str:
        """
        Generate a unique transaction ID.

        In a real system, this would use a database sequence, UUID, or
        distributed ID generator. For this in-memory implementation, we
        use a simple counter.

        Returns:
            A unique transaction ID like "TXN-000001"
        """
        self._transaction_counter += 1
        return f"TXN-{self._transaction_counter:06d}"
