"""
Tests for the Transaction domain model.

These tests verify that the Transaction class behaves correctly as an
immutable value object with proper validation.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest
from datetime import datetime, timedelta

from app.domain.transaction import Transaction


# ──────────────────────────────────────────────
#  Transaction Creation
# ──────────────────────────────────────────────


class TestTransactionCreation:
    """Tests for creating Transaction objects via __init__."""

    def test_create_deposit_transaction(self):
        """A deposit transaction should be created with valid parameters."""
        txn = Transaction(
            "TXN-001",
            "ACC-001",
            "deposit",
            100.0,
            description="Salary deposit"
        )

        assert txn.transaction_id == "TXN-001"
        assert txn.account_number == "ACC-001"
        assert txn.transaction_type == "deposit"
        assert txn.amount == 100.0
        assert txn.description == "Salary deposit"
        assert isinstance(txn.timestamp, datetime)

    def test_create_withdrawal_transaction(self):
        """A withdrawal transaction should be created with valid parameters."""
        txn = Transaction("TXN-002", "ACC-002", "withdrawal", 50.0)

        assert txn.transaction_id == "TXN-002"
        assert txn.account_number == "ACC-002"
        assert txn.transaction_type == "withdrawal"
        assert txn.amount == 50.0

    def test_create_transaction_with_custom_timestamp(self):
        """A transaction can be created with a custom timestamp."""
        custom_time = datetime(2026, 1, 1, 12, 0, 0)
        txn = Transaction("TXN-003", "ACC-003", "deposit", 200.0, timestamp=custom_time)

        assert txn.timestamp == custom_time

    def test_create_transaction_default_timestamp(self):
        """A transaction without timestamp should default to now."""
        before = datetime.now()
        txn = Transaction("TXN-004", "ACC-004", "deposit", 100.0)
        after = datetime.now()

        assert before <= txn.timestamp <= after

    def test_create_transaction_empty_description(self):
        """A transaction with empty description should work."""
        txn = Transaction("TXN-005", "ACC-005", "deposit", 100.0, description="")
        assert txn.description == ""

    def test_create_transaction_strips_description_whitespace(self):
        """Description whitespace should be stripped."""
        txn = Transaction("TXN-006", "ACC-006", "deposit", 100.0, description="  Test  ")
        assert txn.description == "Test"

    def test_create_transaction_empty_id_raises_error(self):
        """An empty transaction ID should raise a ValueError."""
        with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
            Transaction("", "ACC-001", "deposit", 100.0)

    def test_create_transaction_whitespace_id_raises_error(self):
        """A whitespace-only transaction ID should raise a ValueError."""
        with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
            Transaction("   ", "ACC-001", "deposit", 100.0)

    def test_create_transaction_empty_account_number_raises_error(self):
        """An empty account number should raise a ValueError."""
        with pytest.raises(ValueError, match="Account number cannot be empty"):
            Transaction("TXN-007", "", "deposit", 100.0)

    def test_create_transaction_whitespace_account_number_raises_error(self):
        """A whitespace-only account number should raise a ValueError."""
        with pytest.raises(ValueError, match="Account number cannot be empty"):
            Transaction("TXN-008", "   ", "deposit", 100.0)

    def test_create_transaction_invalid_type_raises_error(self):
        """An invalid transaction type should raise a ValueError."""
        with pytest.raises(ValueError, match="Invalid transaction type"):
            Transaction("TXN-009", "ACC-001", "transfer", 100.0)  # type: ignore

    def test_create_transaction_zero_amount_raises_error(self):
        """A zero amount should raise a ValueError."""
        with pytest.raises(ValueError, match="Transaction amount must be positive"):
            Transaction("TXN-010", "ACC-001", "deposit", 0.0)

    def test_create_transaction_negative_amount_raises_error(self):
        """A negative amount should raise a ValueError."""
        with pytest.raises(ValueError, match="Transaction amount must be positive"):
            Transaction("TXN-011", "ACC-001", "deposit", -100.0)


# ──────────────────────────────────────────────
#  Immutability
# ──────────────────────────────────────────────


class TestImmutability:
    """Tests verifying that Transaction is immutable."""

    def test_transaction_id_is_read_only(self):
        """transaction_id should be read-only."""
        txn = Transaction("TXN-100", "ACC-001", "deposit", 100.0)

        with pytest.raises(AttributeError):
            txn.transaction_id = "TXN-999"  # type: ignore

    def test_account_number_is_read_only(self):
        """account_number should be read-only."""
        txn = Transaction("TXN-101", "ACC-001", "deposit", 100.0)

        with pytest.raises(AttributeError):
            txn.account_number = "ACC-999"  # type: ignore

    def test_transaction_type_is_read_only(self):
        """transaction_type should be read-only."""
        txn = Transaction("TXN-102", "ACC-001", "deposit", 100.0)

        with pytest.raises(AttributeError):
            txn.transaction_type = "withdrawal"  # type: ignore

    def test_amount_is_read_only(self):
        """amount should be read-only."""
        txn = Transaction("TXN-103", "ACC-001", "deposit", 100.0)

        with pytest.raises(AttributeError):
            txn.amount = 999.0  # type: ignore

    def test_timestamp_is_read_only(self):
        """timestamp should be read-only."""
        txn = Transaction("TXN-104", "ACC-001", "deposit", 100.0)

        with pytest.raises(AttributeError):
            txn.timestamp = datetime.now()  # type: ignore

    def test_description_is_read_only(self):
        """description should be read-only."""
        txn = Transaction("TXN-105", "ACC-001", "deposit", 100.0)

        with pytest.raises(AttributeError):
            txn.description = "Changed"  # type: ignore


# ──────────────────────────────────────────────
#  Helper Methods
# ──────────────────────────────────────────────


class TestHelperMethods:
    """Tests for is_deposit() and is_withdrawal() methods."""

    def test_is_deposit_returns_true_for_deposit(self):
        """is_deposit() should return True for deposit transactions."""
        txn = Transaction("TXN-200", "ACC-001", "deposit", 100.0)
        assert txn.is_deposit() is True

    def test_is_deposit_returns_false_for_withdrawal(self):
        """is_deposit() should return False for withdrawal transactions."""
        txn = Transaction("TXN-201", "ACC-001", "withdrawal", 100.0)
        assert txn.is_deposit() is False

    def test_is_withdrawal_returns_true_for_withdrawal(self):
        """is_withdrawal() should return True for withdrawal transactions."""
        txn = Transaction("TXN-202", "ACC-001", "withdrawal", 100.0)
        assert txn.is_withdrawal() is True

    def test_is_withdrawal_returns_false_for_deposit(self):
        """is_withdrawal() should return False for deposit transactions."""
        txn = Transaction("TXN-203", "ACC-001", "deposit", 100.0)
        assert txn.is_withdrawal() is False


# ──────────────────────────────────────────────
#  Equality and Hashing
# ──────────────────────────────────────────────


class TestEqualityAndHashing:
    """Tests for __eq__ and __hash__ methods (value object behavior)."""

    def test_equal_transactions_are_equal(self):
        """Two transactions with identical attributes should be equal."""
        timestamp = datetime(2026, 1, 1, 12, 0, 0)
        txn1 = Transaction("TXN-300", "ACC-001", "deposit", 100.0, timestamp, "Test")
        txn2 = Transaction("TXN-300", "ACC-001", "deposit", 100.0, timestamp, "Test")

        assert txn1 == txn2

    def test_different_id_makes_unequal(self):
        """Transactions with different IDs should not be equal."""
        timestamp = datetime(2026, 1, 1, 12, 0, 0)
        txn1 = Transaction("TXN-301", "ACC-001", "deposit", 100.0, timestamp)
        txn2 = Transaction("TXN-302", "ACC-001", "deposit", 100.0, timestamp)

        assert txn1 != txn2

    def test_different_amount_makes_unequal(self):
        """Transactions with different amounts should not be equal."""
        timestamp = datetime(2026, 1, 1, 12, 0, 0)
        txn1 = Transaction("TXN-303", "ACC-001", "deposit", 100.0, timestamp)
        txn2 = Transaction("TXN-303", "ACC-001", "deposit", 200.0, timestamp)

        assert txn1 != txn2

    def test_different_type_makes_unequal(self):
        """Transactions with different types should not be equal."""
        timestamp = datetime(2026, 1, 1, 12, 0, 0)
        txn1 = Transaction("TXN-304", "ACC-001", "deposit", 100.0, timestamp)
        txn2 = Transaction("TXN-304", "ACC-001", "withdrawal", 100.0, timestamp)

        assert txn1 != txn2

    def test_equal_transactions_have_same_hash(self):
        """Equal transactions should have the same hash."""
        timestamp = datetime(2026, 1, 1, 12, 0, 0)
        txn1 = Transaction("TXN-305", "ACC-001", "deposit", 100.0, timestamp, "Test")
        txn2 = Transaction("TXN-305", "ACC-001", "deposit", 100.0, timestamp, "Test")

        assert hash(txn1) == hash(txn2)

    def test_transactions_can_be_added_to_set(self):
        """Transactions can be added to a set (hashable)."""
        txn1 = Transaction("TXN-306", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-307", "ACC-001", "withdrawal", 50.0)

        txn_set = {txn1, txn2}
        assert len(txn_set) == 2
        assert txn1 in txn_set
        assert txn2 in txn_set

    def test_transactions_can_be_dict_keys(self):
        """Transactions can be used as dictionary keys (hashable)."""
        txn = Transaction("TXN-308", "ACC-001", "deposit", 100.0)
        txn_dict = {txn: "metadata"}

        assert txn_dict[txn] == "metadata"

    def test_comparing_with_non_transaction_returns_false(self):
        """Comparing a Transaction with a non-Transaction should return False."""
        txn = Transaction("TXN-309", "ACC-001", "deposit", 100.0)

        assert txn != "not a transaction"
        assert txn != 123
        assert txn != None


# ──────────────────────────────────────────────
#  __repr__
# ──────────────────────────────────────────────


class TestRepr:
    """Tests for the __repr__ method."""

    def test_repr_contains_transaction_info(self):
        """__repr__ should include transaction ID, account, type, and amount."""
        txn = Transaction("TXN-400", "ACC-001", "deposit", 100.0)
        result = repr(txn)

        assert "TXN-400" in result
        assert "ACC-001" in result
        assert "deposit" in result
        assert "100.0" in result
