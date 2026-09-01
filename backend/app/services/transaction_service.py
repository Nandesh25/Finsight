"""
FinSight — Transaction Service (Updated with Repository Pattern)

This module defines the TransactionService class, which coordinates transaction-related
business operations using the Repository Pattern for data access.

Key Architecture Concepts:
    - Service Layer: Orchestrates transaction operations
    - Repository Pattern: Uses repositories for data access
    - Dependency Injection: Repository injected via constructor
    - Separation of Concerns: Service coordinates, repository persists
    - Abstraction: Depends on repository interface, not implementation
"""

from typing import Optional
from datetime import datetime
from app.domain.account import Account
from app.domain.transaction import Transaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository


class TransactionService:
    """
    Service for transaction-related operations.

    This service now uses a repository for data access instead of managing
    storage directly. This demonstrates:
        - Dependency Injection: Repository passed to constructor
        - Separation of Concerns: Service coordinates, repository persists
        - Loose Coupling: Service depends on abstraction (repository interface)

    Updated in Phase 7: Now uses TransactionRepository for persistence.
    """

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        """
        Initialize the TransactionService with repository dependency.

        This is Dependency Injection in action. The service receives
        its dependencies from the outside rather than creating them.

        Args:
            transaction_repository: Repository for transaction data access
        """
        self._transaction_repo = transaction_repository
        self._transaction_counter = 0

    def create_transaction(
        self,
        account: Account,
        transaction_type: TransactionType,
        amount: float,
        description: str = "",
    ) -> Transaction:
        """
        Create a transaction record for an account operation.

        Now persists via repository instead of internal storage.

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

        # Create the Transaction domain object (validation happens here)
        transaction = Transaction(
            transaction_id=transaction_id,
            account_number=account.account_number,
            transaction_type=transaction_type,
            amount=amount,
            timestamp=datetime.now(),
            description=description,
        )

        # Persist via repository
        self._transaction_repo.create(transaction)

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

        Now delegates to repository instead of internal storage.

        Args:
            account_number: The account to retrieve transactions for
            transaction_type: Filter by type ("deposit" or "withdrawal"), None for all
            limit: Maximum number of transactions to return, None for all

        Returns:
            List of Transaction objects, most recent first
        """
        return self._transaction_repo.find_by_account(
            account_number=account_number,
            transaction_type=transaction_type,
            limit=limit,
        )

    def get_transaction_by_id(
        self,
        transaction_id: str,
    ) -> Optional[Transaction]:
        """
        Retrieve a specific transaction by its ID.

        Now retrieves from repository.

        Args:
            transaction_id: The transaction ID to search for

        Returns:
            The Transaction object if found, None otherwise
        """
        return self._transaction_repo.find_by_id(transaction_id)

    def get_transaction_count(self, account_number: str) -> int:
        """
        Get the total number of transactions for an account.

        Now delegates to repository.

        Args:
            account_number: The account to count transactions for

        Returns:
            Number of transactions
        """
        return self._transaction_repo.count_by_account(account_number)

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

        In a real system with multiple service instances, this would
        use a database sequence or distributed ID generator.

        Returns:
            A unique transaction ID like "TXN-000001"
        """
        self._transaction_counter += 1
        return f"TXN-{self._transaction_counter:06d}"
