"""
Tests for the AccountRepository.

These tests verify that the repository correctly handles account persistence
and retrieval operations.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest

from app.domain.account import Account
from app.repositories.account_repository import InMemoryAccountRepository


# ──────────────────────────────────────────────
#  Create Account
# ──────────────────────────────────────────────


class TestCreateAccount:
    """Tests for the create() method."""

    def test_create_account_stores_account(self):
        """Creating an account should store it in the repository."""
        repo = InMemoryAccountRepository()
        account = Account("ACC-001", "savings", balance=100.0)

        created = repo.create(account)

        assert created is account
        assert repo.exists("ACC-001")

    def test_create_multiple_accounts(self):
        """Repository should store multiple accounts."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)

        repo.create(account1)
        repo.create(account2)

        assert repo.count() == 2

    def test_create_duplicate_account_raises_error(self):
        """Creating an account with duplicate number should raise ValueError."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-001", "checking", balance=200.0)

        repo.create(account1)

        with pytest.raises(ValueError, match="already exists"):
            repo.create(account2)


# ──────────────────────────────────────────────
#  Find Account by Account Number
# ──────────────────────────────────────────────


class TestFindAccountByNumber:
    """Tests for the find_by_account_number() method."""

    def test_find_by_account_number_returns_account(self):
        """Finding an existing account should return the account."""
        repo = InMemoryAccountRepository()
        account = Account("ACC-001", "savings", balance=100.0)
        repo.create(account)

        found = repo.find_by_account_number("ACC-001")

        assert found is account

    def test_find_by_account_number_returns_none_if_not_found(self):
        """Finding a non-existent account should return None."""
        repo = InMemoryAccountRepository()

        found = repo.find_by_account_number("ACC-999")

        assert found is None

    def test_find_by_account_number_after_multiple_creates(self):
        """Finding a specific account among multiple should work."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)
        account3 = Account("ACC-003", "savings", balance=300.0)

        repo.create(account1)
        repo.create(account2)
        repo.create(account3)

        found = repo.find_by_account_number("ACC-002")

        assert found is account2


# ──────────────────────────────────────────────
#  Find Accounts by User
# ──────────────────────────────────────────────


class TestFindAccountsByUser:
    """Tests for the find_by_user() method."""

    def test_find_by_user_returns_all_accounts(self):
        """find_by_user() returns all accounts (current implementation)."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)

        repo.create(account1)
        repo.create(account2)

        # Current implementation returns all accounts
        accounts = repo.find_by_user("USER-001")

        assert len(accounts) == 2


# ──────────────────────────────────────────────
#  Update Account
# ──────────────────────────────────────────────


class TestUpdateAccount:
    """Tests for the update() method."""

    def test_update_existing_account(self):
        """Updating an existing account should succeed."""
        repo = InMemoryAccountRepository()
        account = Account("ACC-001", "savings", balance=100.0)
        repo.create(account)

        # Modify account
        account.deposit(50.0)

        # Update in repository
        updated = repo.update(account)

        assert updated is account
        assert updated.balance == 150.0

    def test_update_nonexistent_account_raises_error(self):
        """Updating a non-existent account should raise ValueError."""
        repo = InMemoryAccountRepository()
        account = Account("ACC-999", "savings", balance=100.0)

        with pytest.raises(ValueError, match="does not exist"):
            repo.update(account)


# ──────────────────────────────────────────────
#  Account Exists
# ──────────────────────────────────────────────


class TestAccountExists:
    """Tests for the exists() method."""

    def test_exists_returns_true_for_existing_account(self):
        """exists() should return True for an existing account."""
        repo = InMemoryAccountRepository()
        account = Account("ACC-001", "savings", balance=100.0)
        repo.create(account)

        assert repo.exists("ACC-001") is True

    def test_exists_returns_false_for_nonexistent_account(self):
        """exists() should return False for a non-existent account."""
        repo = InMemoryAccountRepository()

        assert repo.exists("ACC-999") is False


# ──────────────────────────────────────────────
#  Delete Account
# ──────────────────────────────────────────────


class TestDeleteAccount:
    """Tests for the delete() method."""

    def test_delete_removes_account(self):
        """Deleting an account should remove it from the repository."""
        repo = InMemoryAccountRepository()
        account = Account("ACC-001", "savings", balance=100.0)
        repo.create(account)

        result = repo.delete("ACC-001")

        assert result is True
        assert not repo.exists("ACC-001")
        assert repo.count() == 0

    def test_delete_nonexistent_account_returns_false(self):
        """Deleting a non-existent account should return False."""
        repo = InMemoryAccountRepository()

        result = repo.delete("ACC-999")

        assert result is False

    def test_delete_one_of_many(self):
        """Deleting one account should leave others intact."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)
        account3 = Account("ACC-003", "savings", balance=300.0)

        repo.create(account1)
        repo.create(account2)
        repo.create(account3)

        repo.delete("ACC-002")

        assert repo.count() == 2
        assert repo.exists("ACC-001")
        assert not repo.exists("ACC-002")
        assert repo.exists("ACC-003")


# ──────────────────────────────────────────────
#  List All Accounts
# ──────────────────────────────────────────────


class TestListAllAccounts:
    """Tests for the list_all() method."""

    def test_list_all_returns_all_accounts(self):
        """list_all() should return all stored accounts."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)

        repo.create(account1)
        repo.create(account2)

        accounts = repo.list_all()

        assert len(accounts) == 2
        assert account1 in accounts
        assert account2 in accounts

    def test_list_all_empty_repository(self):
        """list_all() should return empty list for empty repository."""
        repo = InMemoryAccountRepository()

        accounts = repo.list_all()

        assert accounts == []


# ──────────────────────────────────────────────
#  Helper Methods
# ──────────────────────────────────────────────


class TestHelperMethods:
    """Tests for helper methods (count, clear)."""

    def test_count_returns_number_of_accounts(self):
        """count() should return the number of accounts."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)

        repo.create(account1)
        repo.create(account2)

        assert repo.count() == 2

    def test_count_empty_repository(self):
        """count() should return 0 for empty repository."""
        repo = InMemoryAccountRepository()

        assert repo.count() == 0

    def test_clear_removes_all_accounts(self):
        """clear() should remove all accounts."""
        repo = InMemoryAccountRepository()
        account1 = Account("ACC-001", "savings", balance=100.0)
        account2 = Account("ACC-002", "checking", balance=200.0)

        repo.create(account1)
        repo.create(account2)

        repo.clear()

        assert repo.count() == 0
        assert repo.list_all() == []
