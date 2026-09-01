"""
Tests for the User domain model.

These tests verify that the User class correctly manages multiple accounts
and enforces proper validation. They demonstrate composition, association,
and object collaboration patterns.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest

from app.domain.account import Account
from app.domain.user import User


# ──────────────────────────────────────────────
#  User Creation
# ──────────────────────────────────────────────


class TestUserCreation:
    """Tests for creating User objects via __init__."""

    def test_create_user_with_valid_data(self):
        """A new user should be created with valid user_id, name, and email."""
        user = User("USER-001", "John Doe", "john@example.com")

        assert user.user_id == "USER-001"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert len(user.accounts) == 0

    def test_create_user_starts_with_empty_accounts(self):
        """A newly created user should have no accounts initially."""
        user = User("USER-002", "Jane Smith", "jane@example.com")
        assert user.list_accounts() == []

    def test_create_user_empty_user_id_raises_error(self):
        """An empty user_id should raise a ValueError."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            User("", "John Doe", "john@example.com")

    def test_create_user_whitespace_user_id_raises_error(self):
        """A whitespace-only user_id should raise a ValueError."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            User("   ", "John Doe", "john@example.com")

    def test_create_user_empty_name_raises_error(self):
        """An empty name should raise a ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            User("USER-003", "", "john@example.com")

    def test_create_user_whitespace_name_raises_error(self):
        """A whitespace-only name should raise a ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            User("USER-004", "   ", "john@example.com")

    def test_create_user_empty_email_raises_error(self):
        """An empty email should raise a ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            User("USER-005", "John Doe", "")

    def test_create_user_whitespace_email_raises_error(self):
        """A whitespace-only email should raise a ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            User("USER-006", "John Doe", "   ")

    def test_create_user_invalid_email_no_at_raises_error(self):
        """An email without @ should raise a ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            User("USER-007", "John Doe", "johnexample.com")

    def test_create_user_invalid_email_no_domain_raises_error(self):
        """An email without a proper domain should raise a ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            User("USER-008", "John Doe", "john@example")


# ──────────────────────────────────────────────
#  Adding Accounts
# ──────────────────────────────────────────────


class TestAddAccount:
    """Tests for the add_account() method."""

    def test_add_account_increases_account_count(self):
        """Adding an account should increase the user's account count."""
        user = User("USER-100", "Alice Brown", "alice@example.com")
        account = Account("ACC-001", "savings", balance=100.0)

        user.add_account(account)

        assert len(user.accounts) == 1
        assert account in user.accounts

    def test_add_account_returns_none(self):
        """add_account() should not return a value (returns None)."""
        user = User("USER-101", "Bob Green", "bob@example.com")
        account = Account("ACC-002", "checking")

        result = user.add_account(account)

        assert result is None

    def test_add_multiple_accounts(self):
        """A user can own multiple accounts."""
        user = User("USER-102", "Carol White", "carol@example.com")
        account1 = Account("ACC-003", "savings", balance=500.0)
        account2 = Account("ACC-004", "checking", balance=1000.0)

        user.add_account(account1)
        user.add_account(account2)

        assert len(user.accounts) == 2
        assert account1 in user.accounts
        assert account2 in user.accounts

    def test_add_account_none_raises_error(self):
        """Adding None as an account should raise a ValueError."""
        user = User("USER-103", "Dave Black", "dave@example.com")

        with pytest.raises(ValueError, match="Cannot add None as an account"):
            user.add_account(None)

    def test_add_duplicate_account_object_raises_error(self):
        """Adding the same account object twice should raise a ValueError."""
        user = User("USER-104", "Eve Blue", "eve@example.com")
        account = Account("ACC-005", "savings")

        user.add_account(account)

        with pytest.raises(ValueError, match="already belongs to this user"):
            user.add_account(account)

    def test_add_account_with_duplicate_number_raises_error(self):
        """Adding a different account with the same number should raise a ValueError."""
        user = User("USER-105", "Frank Red", "frank@example.com")
        account1 = Account("ACC-006", "savings")
        account2 = Account("ACC-006", "checking")  # Same number, different object

        user.add_account(account1)

        with pytest.raises(ValueError, match="already exists for this user"):
            user.add_account(account2)


# ──────────────────────────────────────────────
#  Removing Accounts
# ──────────────────────────────────────────────


class TestRemoveAccount:
    """Tests for the remove_account() method."""

    def test_remove_account_decreases_account_count(self):
        """Removing an account should decrease the user's account count."""
        user = User("USER-200", "Grace Yellow", "grace@example.com")
        account = Account("ACC-007", "savings")
        user.add_account(account)

        user.remove_account("ACC-007")

        assert len(user.accounts) == 0
        assert account not in user.accounts

    def test_remove_account_returns_removed_account(self):
        """remove_account() should return the removed Account object."""
        user = User("USER-201", "Henry Purple", "henry@example.com")
        account = Account("ACC-008", "checking", balance=250.0)
        user.add_account(account)

        removed = user.remove_account("ACC-008")

        assert removed is account
        assert removed.account_number == "ACC-008"
        assert removed.balance == 250.0

    def test_remove_account_from_multiple_accounts(self):
        """Removing one account should leave others intact."""
        user = User("USER-202", "Ivy Orange", "ivy@example.com")
        account1 = Account("ACC-009", "savings")
        account2 = Account("ACC-010", "checking")
        account3 = Account("ACC-011", "savings")

        user.add_account(account1)
        user.add_account(account2)
        user.add_account(account3)

        user.remove_account("ACC-010")

        assert len(user.accounts) == 2
        assert account1 in user.accounts
        assert account2 not in user.accounts
        assert account3 in user.accounts

    def test_remove_nonexistent_account_raises_error(self):
        """Removing an account that doesn't exist should raise a ValueError."""
        user = User("USER-203", "Jack Pink", "jack@example.com")
        account = Account("ACC-012", "savings")
        user.add_account(account)

        with pytest.raises(ValueError, match="No account found"):
            user.remove_account("ACC-999")

    def test_remove_account_from_empty_user_raises_error(self):
        """Removing from a user with no accounts should raise a ValueError."""
        user = User("USER-204", "Kate Silver", "kate@example.com")

        with pytest.raises(ValueError, match="No account found"):
            user.remove_account("ACC-013")


# ──────────────────────────────────────────────
#  Finding Accounts
# ──────────────────────────────────────────────


class TestFindAccount:
    """Tests for the find_account() method."""

    def test_find_account_returns_matching_account(self):
        """find_account() should return the account with the matching number."""
        user = User("USER-300", "Leo Gold", "leo@example.com")
        account1 = Account("ACC-014", "savings", balance=300.0)
        account2 = Account("ACC-015", "checking", balance=700.0)

        user.add_account(account1)
        user.add_account(account2)

        found = user.find_account("ACC-015")

        assert found is account2
        assert found.balance == 700.0

    def test_find_account_returns_none_if_not_found(self):
        """find_account() should return None if no account matches."""
        user = User("USER-301", "Mia Bronze", "mia@example.com")
        account = Account("ACC-016", "savings")
        user.add_account(account)

        found = user.find_account("ACC-999")

        assert found is None

    def test_find_account_in_empty_user_returns_none(self):
        """find_account() should return None if the user has no accounts."""
        user = User("USER-302", "Noah Copper", "noah@example.com")

        found = user.find_account("ACC-017")

        assert found is None

    def test_find_account_first_match_in_multiple_accounts(self):
        """find_account() should return the first account that matches."""
        user = User("USER-303", "Olivia Steel", "olivia@example.com")
        account1 = Account("ACC-018", "savings")
        account2 = Account("ACC-019", "checking")
        account3 = Account("ACC-020", "savings")

        user.add_account(account1)
        user.add_account(account2)
        user.add_account(account3)

        found = user.find_account("ACC-019")

        assert found is account2


# ──────────────────────────────────────────────
#  Listing Accounts
# ──────────────────────────────────────────────


class TestListAccounts:
    """Tests for the list_accounts() method and accounts property."""

    def test_list_accounts_returns_all_accounts(self):
        """list_accounts() should return all accounts owned by the user."""
        user = User("USER-400", "Paul Iron", "paul@example.com")
        account1 = Account("ACC-021", "savings")
        account2 = Account("ACC-022", "checking")

        user.add_account(account1)
        user.add_account(account2)

        accounts = user.list_accounts()

        assert len(accounts) == 2
        assert account1 in accounts
        assert account2 in accounts

    def test_list_accounts_returns_empty_list_for_no_accounts(self):
        """list_accounts() should return an empty list if user has no accounts."""
        user = User("USER-401", "Quinn Brass", "quinn@example.com")

        accounts = user.list_accounts()

        assert accounts == []

    def test_accounts_property_returns_copy(self):
        """The accounts property should return a copy, not the internal list."""
        user = User("USER-402", "Rachel Tin", "rachel@example.com")
        account = Account("ACC-023", "savings")
        user.add_account(account)

        accounts_copy = user.accounts
        accounts_copy.clear()

        # The user's internal list should still have the account
        assert len(user.accounts) == 1

    def test_list_accounts_matches_accounts_property(self):
        """list_accounts() and accounts property should return the same content."""
        user = User("USER-403", "Sam Zinc", "sam@example.com")
        account1 = Account("ACC-024", "savings")
        account2 = Account("ACC-025", "checking")

        user.add_account(account1)
        user.add_account(account2)

        assert user.list_accounts() == user.accounts


# ──────────────────────────────────────────────
#  Multiple Accounts Per User
# ──────────────────────────────────────────────


class TestMultipleAccounts:
    """Tests for users owning multiple accounts."""

    def test_user_can_own_multiple_savings_accounts(self):
        """A user can own multiple accounts of the same type."""
        user = User("USER-500", "Tina Aluminum", "tina@example.com")
        savings1 = Account("ACC-026", "savings", balance=1000.0)
        savings2 = Account("ACC-027", "savings", balance=2000.0)

        user.add_account(savings1)
        user.add_account(savings2)

        assert len(user.accounts) == 2
        assert all(acc.account_type == "savings" for acc in user.accounts)

    def test_user_can_own_mixed_account_types(self):
        """A user can own both savings and checking accounts."""
        user = User("USER-501", "Uma Nickel", "uma@example.com")
        savings = Account("ACC-028", "savings")
        checking = Account("ACC-029", "checking")

        user.add_account(savings)
        user.add_account(checking)

        account_types = [acc.account_type for acc in user.accounts]
        assert "savings" in account_types
        assert "checking" in account_types

    def test_user_with_many_accounts(self):
        """A user can own many accounts."""
        user = User("USER-502", "Victor Cobalt", "victor@example.com")

        for i in range(10):
            account_type = "savings" if i % 2 == 0 else "checking"
            account = Account(f"ACC-{100 + i}", account_type, balance=float(i * 100))
            user.add_account(account)

        assert len(user.accounts) == 10


# ──────────────────────────────────────────────
#  Account Validation & Business Rules
# ──────────────────────────────────────────────


class TestAccountValidation:
    """Tests verifying that User enforces account validation."""

    def test_user_cannot_directly_modify_account_balance(self):
        """User should not be able to directly set an account's balance."""
        user = User("USER-600", "Wendy Titanium", "wendy@example.com")
        account = Account("ACC-030", "savings", balance=500.0)
        user.add_account(account)

        # Try to modify the account's balance directly (should fail)
        with pytest.raises(AttributeError):
            account.balance = 9999.0

        # Balance should remain unchanged
        assert account.balance == 500.0

    def test_user_delegates_deposit_to_account(self):
        """User should delegate deposit operations to the Account object."""
        user = User("USER-601", "Xander Platinum", "xander@example.com")
        account = Account("ACC-031", "savings", balance=100.0)
        user.add_account(account)

        # User finds the account and calls deposit on it
        found_account = user.find_account("ACC-031")
        found_account.deposit(50.0)

        assert found_account.balance == 150.0

    def test_user_delegates_withdraw_to_account(self):
        """User should delegate withdrawal operations to the Account object."""
        user = User("USER-602", "Yara Palladium", "yara@example.com")
        account = Account("ACC-032", "checking", balance=200.0)
        user.add_account(account)

        # User finds the account and calls withdraw on it
        found_account = user.find_account("ACC-032")
        found_account.withdraw(75.0)

        assert found_account.balance == 125.0

    def test_account_enforces_own_validation_rules(self):
        """Account should enforce its own business rules, not User."""
        user = User("USER-603", "Zara Rhodium", "zara@example.com")
        account = Account("ACC-033", "savings", balance=50.0)
        user.add_account(account)

        # Try to withdraw more than the balance (Account should reject)
        found_account = user.find_account("ACC-033")
        with pytest.raises(ValueError, match="Insufficient balance"):
            found_account.withdraw(100.0)

        # Balance should remain unchanged
        assert found_account.balance == 50.0


# ──────────────────────────────────────────────
#  Invalid Operations
# ──────────────────────────────────────────────


class TestInvalidOperations:
    """Tests for invalid operations on User."""

    def test_remove_same_account_twice_raises_error(self):
        """Removing the same account twice should raise a ValueError on the second call."""
        user = User("USER-700", "Adam Iridium", "adam@example.com")
        account = Account("ACC-034", "savings")
        user.add_account(account)

        user.remove_account("ACC-034")

        with pytest.raises(ValueError, match="No account found"):
            user.remove_account("ACC-034")

    def test_find_after_remove_returns_none(self):
        """Finding an account after removing it should return None."""
        user = User("USER-701", "Beth Osmium", "beth@example.com")
        account = Account("ACC-035", "checking")
        user.add_account(account)

        user.remove_account("ACC-035")
        found = user.find_account("ACC-035")

        assert found is None


# ──────────────────────────────────────────────
#  Total Balance Calculation
# ──────────────────────────────────────────────


class TestGetTotalBalance:
    """Tests for the get_total_balance() method."""

    def test_get_total_balance_single_account(self):
        """Total balance with one account should equal that account's balance."""
        user = User("USER-800", "Carl Ruthenium", "carl@example.com")
        account = Account("ACC-036", "savings", balance=750.0)
        user.add_account(account)

        assert user.get_total_balance() == 750.0

    def test_get_total_balance_multiple_accounts(self):
        """Total balance should sum all account balances."""
        user = User("USER-801", "Dana Tungsten", "dana@example.com")
        account1 = Account("ACC-037", "savings", balance=500.0)
        account2 = Account("ACC-038", "checking", balance=300.0)
        account3 = Account("ACC-039", "savings", balance=200.0)

        user.add_account(account1)
        user.add_account(account2)
        user.add_account(account3)

        assert user.get_total_balance() == 1000.0

    def test_get_total_balance_no_accounts(self):
        """Total balance with no accounts should be 0.0."""
        user = User("USER-802", "Ella Rhenium", "ella@example.com")

        assert user.get_total_balance() == 0.0

    def test_get_total_balance_with_zero_balance_accounts(self):
        """Total balance should correctly handle accounts with zero balance."""
        user = User("USER-803", "Finn Hafnium", "finn@example.com")
        account1 = Account("ACC-040", "savings", balance=0.0)
        account2 = Account("ACC-041", "checking", balance=100.0)

        user.add_account(account1)
        user.add_account(account2)

        assert user.get_total_balance() == 100.0

    def test_get_total_balance_updates_after_transactions(self):
        """Total balance should reflect changes from deposits and withdrawals."""
        user = User("USER-804", "Gina Tantalum", "gina@example.com")
        account1 = Account("ACC-042", "savings", balance=500.0)
        account2 = Account("ACC-043", "checking", balance=500.0)

        user.add_account(account1)
        user.add_account(account2)

        # Make some transactions
        account1.deposit(100.0)
        account2.withdraw(50.0)

        assert user.get_total_balance() == 1050.0  # 600 + 450


# ──────────────────────────────────────────────
#  __repr__
# ──────────────────────────────────────────────


class TestRepr:
    """Tests for the __repr__ method."""

    def test_repr_contains_user_info(self):
        """__repr__ should include user_id, name, email, and account count."""
        user = User("USER-900", "Hugo Vanadium", "hugo@example.com")
        result = repr(user)

        assert "USER-900" in result
        assert "Hugo Vanadium" in result
        assert "hugo@example.com" in result
        assert "accounts=0" in result

    def test_repr_shows_account_count(self):
        """__repr__ should show the correct number of accounts."""
        user = User("USER-901", "Iris Chromium", "iris@example.com")
        account1 = Account("ACC-044", "savings")
        account2 = Account("ACC-045", "checking")

        user.add_account(account1)
        user.add_account(account2)

        result = repr(user)
        assert "accounts=2" in result
