"""
Tests for the TransactionRepository.

These tests verify that the repository correctly handles transaction persistence
and retrieval operations.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest
from datetime import datetime

from app.domain.transaction import Transaction
from app.repositories.transaction_repository import InMemoryTransactionRepository


# ──────────────────────────────────────────────
#  Create Transaction
# ──────────────────────────────────────────────


class TestCreateTransaction:
    """Tests for the create() method."""

    def test_create_transaction_stores_transaction(self):
        """Creating a transaction should store it in the repository."""
        repo = InMemoryTransactionRepository()
        txn = Transaction("TXN-001", "ACC-001", "deposit", 100.0)

        created = repo.create(txn)

        assert created is txn
        assert repo.exists("TXN-001")

    def test_create_multiple_transactions(self):
        """Repository should store multiple transactions."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-001", "withdrawal", 50.0)

        repo.create(txn1)
        repo.create(txn2)

        assert repo.count() == 2

    def test_create_duplicate_transaction_raises_error(self):
        """Creating a transaction with duplicate ID should raise ValueError."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-001", "ACC-002", "deposit", 200.0)

        repo.create(txn1)

        with pytest.raises(ValueError, match="already exists"):
            repo.create(txn2)

    def test_create_builds_secondary_index(self):
        """Creating transactions should build account-based index."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-001", "withdrawal", 50.0)

        repo.create(txn1)
        repo.create(txn2)

        transactions = repo.find_by_account("ACC-001")
        assert len(transactions) == 2


# ──────────────────────────────────────────────
#  Find Transaction by ID
# ──────────────────────────────────────────────


class TestFindTransactionById:
    """Tests for the find_by_id() method."""

    def test_find_by_id_returns_transaction(self):
        """Finding an existing transaction should return the transaction."""
        repo = InMemoryTransactionRepository()
        txn = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        repo.create(txn)

        found = repo.find_by_id("TXN-001")

        assert found is txn

    def test_find_by_id_returns_none_if_not_found(self):
        """Finding a non-existent transaction should return None."""
        repo = InMemoryTransactionRepository()

        found = repo.find_by_id("TXN-999")

        assert found is None


# ──────────────────────────────────────────────
#  Find Transactions by Account
# ──────────────────────────────────────────────


class TestFindTransactionsByAccount:
    """Tests for the find_by_account() method."""

    def test_find_by_account_returns_all_transactions(self):
        """find_by_account() should return all transactions for an account."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-001", "withdrawal", 50.0)
        txn3 = Transaction("TXN-003", "ACC-002", "deposit", 200.0)

        repo.create(txn1)
        repo.create(txn2)
        repo.create(txn3)

        transactions = repo.find_by_account("ACC-001")

        assert len(transactions) == 2
        assert txn1 in transactions
        assert txn2 in transactions
        assert txn3 not in transactions

    def test_find_by_account_filter_by_type_deposit(self):
        """find_by_account() should filter by deposit type."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-001", "withdrawal", 50.0)
        txn3 = Transaction("TXN-003", "ACC-001", "deposit", 75.0)

        repo.create(txn1)
        repo.create(txn2)
        repo.create(txn3)

        transactions = repo.find_by_account("ACC-001", transaction_type="deposit")

        assert len(transactions) == 2
        assert txn1 in transactions
        assert txn3 in transactions
        assert txn2 not in transactions

    def test_find_by_account_filter_by_type_withdrawal(self):
        """find_by_account() should filter by withdrawal type."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-001", "withdrawal", 50.0)
        txn3 = Transaction("TXN-003", "ACC-001", "deposit", 75.0)

        repo.create(txn1)
        repo.create(txn2)
        repo.create(txn3)

        transactions = repo.find_by_account("ACC-001", transaction_type="withdrawal")

        assert len(transactions) == 1
        assert transactions[0] is txn2

    def test_find_by_account_with_limit(self):
        """find_by_account() should limit results."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 10.0)
        txn2 = Transaction("TXN-002", "ACC-001", "deposit", 20.0)
        txn3 = Transaction("TXN-003", "ACC-001", "deposit", 30.0)

        repo.create(txn1)
        repo.create(txn2)
        repo.create(txn3)

        transactions = repo.find_by_account("ACC-001", limit=2)

        assert len(transactions) == 2

    def test_find_by_account_sorted_by_timestamp(self):
        """find_by_account() should return transactions sorted by timestamp, most recent first."""
        repo = InMemoryTransactionRepository()
        timestamp1 = datetime(2026, 1, 1, 10, 0, 0)
        timestamp2 = datetime(2026, 1, 1, 11, 0, 0)
        timestamp3 = datetime(2026, 1, 1, 12, 0, 0)

        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 10.0, timestamp=timestamp1)
        txn2 = Transaction("TXN-002", "ACC-001", "deposit", 20.0, timestamp=timestamp2)
        txn3 = Transaction("TXN-003", "ACC-001", "deposit", 30.0, timestamp=timestamp3)

        repo.create(txn1)
        repo.create(txn2)
        repo.create(txn3)

        transactions = repo.find_by_account("ACC-001")

        # Most recent first
        assert transactions[0] is txn3
        assert transactions[1] is txn2
        assert transactions[2] is txn1

    def test_find_by_account_empty_result(self):
        """find_by_account() should return empty list if no transactions."""
        repo = InMemoryTransactionRepository()

        transactions = repo.find_by_account("ACC-999")

        assert transactions == []


# ──────────────────────────────────────────────
#  Transaction Exists
# ──────────────────────────────────────────────


class TestTransactionExists:
    """Tests for the exists() method."""

    def test_exists_returns_true_for_existing_transaction(self):
        """exists() should return True for an existing transaction."""
        repo = InMemoryTransactionRepository()
        txn = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        repo.create(txn)

        assert repo.exists("TXN-001") is True

    def test_exists_returns_false_for_nonexistent_transaction(self):
        """exists() should return False for a non-existent transaction."""
        repo = InMemoryTransactionRepository()

        assert repo.exists("TXN-999") is False


# ──────────────────────────────────────────────
#  List All Transactions
# ──────────────────────────────────────────────


class TestListAllTransactions:
    """Tests for the list_all() method."""

    def test_list_all_returns_all_transactions(self):
        """list_all() should return all stored transactions."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-002", "withdrawal", 50.0)

        repo.create(txn1)
        repo.create(txn2)

        transactions = repo.list_all()

        assert len(transactions) == 2
        assert txn1 in transactions
        assert txn2 in transactions

    def test_list_all_empty_repository(self):
        """list_all() should return empty list for empty repository."""
        repo = InMemoryTransactionRepository()

        transactions = repo.list_all()

        assert transactions == []


# ──────────────────────────────────────────────
#  Count Transactions by Account
# ──────────────────────────────────────────────


class TestCountTransactionsByAccount:
    """Tests for the count_by_account() method."""

    def test_count_by_account_returns_count(self):
        """count_by_account() should return the number of transactions."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-001", "withdrawal", 50.0)
        txn3 = Transaction("TXN-003", "ACC-002", "deposit", 200.0)

        repo.create(txn1)
        repo.create(txn2)
        repo.create(txn3)

        count = repo.count_by_account("ACC-001")

        assert count == 2

    def test_count_by_account_empty_account(self):
        """count_by_account() should return 0 for account with no transactions."""
        repo = InMemoryTransactionRepository()

        count = repo.count_by_account("ACC-999")

        assert count == 0


# ──────────────────────────────────────────────
#  Helper Methods
# ──────────────────────────────────────────────


class TestHelperMethods:
    """Tests for helper methods (count, clear)."""

    def test_count_returns_total_transactions(self):
        """count() should return total number of transactions."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-002", "withdrawal", 50.0)

        repo.create(txn1)
        repo.create(txn2)

        assert repo.count() == 2

    def test_count_empty_repository(self):
        """count() should return 0 for empty repository."""
        repo = InMemoryTransactionRepository()

        assert repo.count() == 0

    def test_clear_removes_all_transactions(self):
        """clear() should remove all transactions."""
        repo = InMemoryTransactionRepository()
        txn1 = Transaction("TXN-001", "ACC-001", "deposit", 100.0)
        txn2 = Transaction("TXN-002", "ACC-002", "withdrawal", 50.0)

        repo.create(txn1)
        repo.create(txn2)

        repo.clear()

        assert repo.count() == 0
        assert repo.list_all() == []
