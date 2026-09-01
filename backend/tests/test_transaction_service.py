"""
Tests for the TransactionService.

These tests verify that TransactionService correctly coordinates transaction
operations and interacts properly with Account domain objects.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest
from datetime import datetime

from app.domain.account import Account
from app.domain.transaction import Transaction
from app.services.transaction_service import TransactionService


# ──────────────────────────────────────────────
#  Transaction Creation
# ──────────────────────────────────────────────


class TestCreateTransaction:
    """Tests for the create_transaction() method."""

    def test_create_deposit_transaction(self):
        """Creating a deposit transaction should create and store it."""
        service = TransactionService()
        account = Account("ACC-001", "savings", balance=100.0)

        txn = service.create_transaction(account, "deposit", 50.0, "Salary")

        assert txn.account_number == "ACC-001"
        assert txn.transaction_type == "deposit"
        assert txn.amount == 50.0
        assert txn.description == "Salary"
        assert isinstance(txn.timestamp, datetime)

    def test_create_withdrawal_transaction(self):
        """Creating a withdrawal transaction should create and store it."""
        service = TransactionService()
        account = Account("ACC-002", "checking", balance=200.0)

        txn = service.create_transaction(account, "withdrawal", 75.0, "ATM")

        assert txn.account_number == "ACC-002"
        assert txn.transaction_type == "withdrawal"
        assert txn.amount == 75.0
        assert txn.description == "ATM"

    def test_create_transaction_generates_unique_ids(self):
        """Each transaction should have a unique ID."""
        service = TransactionService()
        account = Account("ACC-003", "savings", balance=100.0)

        txn1 = service.create_transaction(account, "deposit", 50.0)
        txn2 = service.create_transaction(account, "deposit", 25.0)

        assert txn1.transaction_id != txn2.transaction_id

    def test_create_transaction_invalid_amount_raises_error(self):
        """Creating a transaction with invalid amount should raise ValueError."""
        service = TransactionService()
        account = Account("ACC-004", "savings", balance=100.0)

        with pytest.raises(ValueError, match="Transaction amount must be positive"):
            service.create_transaction(account, "deposit", -50.0)


# ──────────────────────────────────────────────
#  Transaction Validation
# ──────────────────────────────────────────────


class TestValidateTransaction:
    """Tests for the validate_transaction() method."""

    def test_validate_valid_deposit(self):
        """Validating a valid deposit should return (True, None)."""
        service = TransactionService()
        account = Account("ACC-100", "savings", balance=100.0)

        is_valid, error = service.validate_transaction(account, "deposit", 50.0)

        assert is_valid is True
        assert error is None

    def test_validate_valid_withdrawal(self):
        """Validating a valid withdrawal should return (True, None)."""
        service = TransactionService()
        account = Account("ACC-101", "checking", balance=200.0)

        is_valid, error = service.validate_transaction(account, "withdrawal", 100.0)

        assert is_valid is True
        assert error is None

    def test_validate_withdrawal_insufficient_balance(self):
        """Validating withdrawal with insufficient balance should return (False, error)."""
        service = TransactionService()
        account = Account("ACC-102", "savings", balance=50.0)

        is_valid, error = service.validate_transaction(account, "withdrawal", 100.0)

        assert is_valid is False
        assert "Insufficient balance" in error

    def test_validate_zero_amount(self):
        """Validating zero amount should return (False, error)."""
        service = TransactionService()
        account = Account("ACC-103", "savings", balance=100.0)

        is_valid, error = service.validate_transaction(account, "deposit", 0.0)

        assert is_valid is False
        assert "must be positive" in error

    def test_validate_negative_amount(self):
        """Validating negative amount should return (False, error)."""
        service = TransactionService()
        account = Account("ACC-104", "savings", balance=100.0)

        is_valid, error = service.validate_transaction(account, "withdrawal", -50.0)

        assert is_valid is False
        assert "must be positive" in error


# ──────────────────────────────────────────────
#  Get Transactions
# ──────────────────────────────────────────────


class TestGetTransactions:
    """Tests for the get_transactions() method."""

    def test_get_transactions_returns_all_transactions(self):
        """get_transactions() should return all transactions for an account."""
        service = TransactionService()
        account = Account("ACC-200", "savings", balance=100.0)

        txn1 = service.create_transaction(account, "deposit", 50.0)
        txn2 = service.create_transaction(account, "withdrawal", 25.0)
        txn3 = service.create_transaction(account, "deposit", 100.0)

        transactions = service.get_transactions("ACC-200")

        assert len(transactions) == 3
        # Most recent first
        assert transactions[0] == txn3
        assert transactions[1] == txn2
        assert transactions[2] == txn1

    def test_get_transactions_filter_by_type_deposit(self):
        """get_transactions() should filter by deposit type."""
        service = TransactionService()
        account = Account("ACC-201", "checking", balance=500.0)

        txn1 = service.create_transaction(account, "deposit", 50.0)
        service.create_transaction(account, "withdrawal", 25.0)
        txn3 = service.create_transaction(account, "deposit", 100.0)

        transactions = service.get_transactions("ACC-201", transaction_type="deposit")

        assert len(transactions) == 2
        assert txn1 in transactions
        assert txn3 in transactions

    def test_get_transactions_filter_by_type_withdrawal(self):
        """get_transactions() should filter by withdrawal type."""
        service = TransactionService()
        account = Account("ACC-202", "savings", balance=500.0)

        service.create_transaction(account, "deposit", 50.0)
        txn2 = service.create_transaction(account, "withdrawal", 25.0)
        service.create_transaction(account, "deposit", 100.0)

        transactions = service.get_transactions("ACC-202", transaction_type="withdrawal")

        assert len(transactions) == 1
        assert transactions[0] == txn2

    def test_get_transactions_with_limit(self):
        """get_transactions() should limit the number of results."""
        service = TransactionService()
        account = Account("ACC-203", "savings", balance=500.0)

        service.create_transaction(account, "deposit", 10.0)
        service.create_transaction(account, "deposit", 20.0)
        service.create_transaction(account, "deposit", 30.0)
        txn4 = service.create_transaction(account, "deposit", 40.0)

        transactions = service.get_transactions("ACC-203", limit=2)

        assert len(transactions) == 2
        # Most recent first
        assert transactions[0] == txn4

    def test_get_transactions_empty_account(self):
        """get_transactions() should return empty list for account with no transactions."""
        service = TransactionService()

        transactions = service.get_transactions("ACC-999999")

        assert transactions == []

    def test_get_transactions_sorted_by_timestamp(self):
        """get_transactions() should return transactions sorted by timestamp, most recent first."""
        service = TransactionService()
        account = Account("ACC-204", "savings", balance=500.0)

        txn1 = service.create_transaction(account, "deposit", 10.0)
        txn2 = service.create_transaction(account, "deposit", 20.0)
        txn3 = service.create_transaction(account, "deposit", 30.0)

        transactions = service.get_transactions("ACC-204")

        assert transactions[0].timestamp >= transactions[1].timestamp
        assert transactions[1].timestamp >= transactions[2].timestamp


# ──────────────────────────────────────────────
#  Get Transaction by ID
# ──────────────────────────────────────────────


class TestGetTransactionById:
    """Tests for the get_transaction_by_id() method."""

    def test_get_transaction_by_id_returns_transaction(self):
        """get_transaction_by_id() should return the transaction if found."""
        service = TransactionService()
        account = Account("ACC-300", "savings", balance=100.0)

        txn = service.create_transaction(account, "deposit", 50.0)

        found = service.get_transaction_by_id(txn.transaction_id)

        assert found == txn

    def test_get_transaction_by_id_returns_none_if_not_found(self):
        """get_transaction_by_id() should return None if transaction not found."""
        service = TransactionService()

        found = service.get_transaction_by_id("TXN-999999")

        assert found is None


# ──────────────────────────────────────────────
#  Transaction Statistics
# ──────────────────────────────────────────────


class TestTransactionStatistics:
    """Tests for transaction statistic methods."""

    def test_get_transaction_count(self):
        """get_transaction_count() should return the number of transactions."""
        service = TransactionService()
        account = Account("ACC-400", "savings", balance=500.0)

        service.create_transaction(account, "deposit", 50.0)
        service.create_transaction(account, "withdrawal", 25.0)
        service.create_transaction(account, "deposit", 100.0)

        count = service.get_transaction_count("ACC-400")

        assert count == 3

    def test_get_transaction_count_empty_account(self):
        """get_transaction_count() should return 0 for account with no transactions."""
        service = TransactionService()

        count = service.get_transaction_count("ACC-999999")

        assert count == 0

    def test_get_total_deposited(self):
        """get_total_deposited() should sum all deposit amounts."""
        service = TransactionService()
        account = Account("ACC-401", "savings", balance=500.0)

        service.create_transaction(account, "deposit", 50.0)
        service.create_transaction(account, "withdrawal", 25.0)
        service.create_transaction(account, "deposit", 100.0)

        total = service.get_total_deposited("ACC-401")

        assert total == 150.0

    def test_get_total_withdrawn(self):
        """get_total_withdrawn() should sum all withdrawal amounts."""
        service = TransactionService()
        account = Account("ACC-402", "checking", balance=500.0)

        service.create_transaction(account, "deposit", 50.0)
        service.create_transaction(account, "withdrawal", 25.0)
        service.create_transaction(account, "withdrawal", 75.0)

        total = service.get_total_withdrawn("ACC-402")

        assert total == 100.0


# ──────────────────────────────────────────────
#  Record Deposit and Withdrawal
# ──────────────────────────────────────────────


class TestRecordDepositAndWithdrawal:
    """Tests for record_deposit() and record_withdrawal() convenience methods."""

    def test_record_deposit_updates_balance_and_creates_transaction(self):
        """record_deposit() should update account balance and create transaction."""
        service = TransactionService()
        account = Account("ACC-500", "savings", balance=100.0)

        txn, new_balance = service.record_deposit(account, 50.0, "Salary")

        assert new_balance == 150.0
        assert account.balance == 150.0
        assert txn.transaction_type == "deposit"
        assert txn.amount == 50.0
        assert txn.description == "Salary"

    def test_record_withdrawal_updates_balance_and_creates_transaction(self):
        """record_withdrawal() should update account balance and create transaction."""
        service = TransactionService()
        account = Account("ACC-501", "checking", balance=200.0)

        txn, new_balance = service.record_withdrawal(account, 75.0, "ATM")

        assert new_balance == 125.0
        assert account.balance == 125.0
        assert txn.transaction_type == "withdrawal"
        assert txn.amount == 75.0
        assert txn.description == "ATM"

    def test_record_deposit_invalid_amount_raises_error(self):
        """record_deposit() should raise error for invalid amount."""
        service = TransactionService()
        account = Account("ACC-502", "savings", balance=100.0)

        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            service.record_deposit(account, -50.0)

    def test_record_withdrawal_insufficient_balance_raises_error(self):
        """record_withdrawal() should raise error for insufficient balance."""
        service = TransactionService()
        account = Account("ACC-503", "savings", balance=50.0)

        with pytest.raises(ValueError, match="Insufficient balance"):
            service.record_withdrawal(account, 100.0)

    def test_record_deposit_transaction_is_stored(self):
        """Transaction created by record_deposit() should be stored and retrievable."""
        service = TransactionService()
        account = Account("ACC-504", "savings", balance=100.0)

        txn, _ = service.record_deposit(account, 50.0)

        transactions = service.get_transactions("ACC-504")
        assert len(transactions) == 1
        assert transactions[0] == txn

    def test_record_withdrawal_transaction_is_stored(self):
        """Transaction created by record_withdrawal() should be stored and retrievable."""
        service = TransactionService()
        account = Account("ACC-505", "checking", balance=200.0)

        txn, _ = service.record_withdrawal(account, 75.0)

        transactions = service.get_transactions("ACC-505")
        assert len(transactions) == 1
        assert transactions[0] == txn


# ──────────────────────────────────────────────
#  Service Independence
# ──────────────────────────────────────────────


class TestServiceIndependence:
    """Tests verifying service independence from other services."""

    def test_multiple_service_instances_have_independent_storage(self):
        """Different service instances should have independent transaction storage."""
        service1 = TransactionService()
        service2 = TransactionService()

        account1 = Account("ACC-600", "savings", balance=100.0)
        account2 = Account("ACC-601", "checking", balance=200.0)

        service1.create_transaction(account1, "deposit", 50.0)
        service2.create_transaction(account2, "deposit", 75.0)

        # Each service has its own transactions
        assert len(service1.get_transactions("ACC-600")) == 1
        assert len(service1.get_transactions("ACC-601")) == 0
        assert len(service2.get_transactions("ACC-600")) == 0
        assert len(service2.get_transactions("ACC-601")) == 1

    def test_service_does_not_modify_account_on_create_transaction(self):
        """create_transaction() should NOT modify account balance."""
        service = TransactionService()
        account = Account("ACC-602", "savings", balance=100.0)

        service.create_transaction(account, "deposit", 50.0)

        # Balance should remain unchanged
        assert account.balance == 100.0
