"""
Tests for the Account domain model.

These tests verify that the Account class behaves correctly in both
normal and edge-case scenarios. Each test is independent — it creates
its own Account object, so tests never interfere with each other.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest

from app.domain.account import Account


# ──────────────────────────────────────────────
#  Account Creation
# ──────────────────────────────────────────────


class TestAccountCreation:
    """Tests for creating Account objects via __init__."""

    def test_create_savings_account_with_default_balance(self):
        """A new savings account should start with balance 0.0 by default."""
        account = Account("ACC-001", "savings")

        assert account.account_number == "ACC-001"
        assert account.account_type == "savings"
        assert account.balance == 0.0

    def test_create_checking_account_with_initial_balance(self):
        """A checking account can be created with an explicit starting balance."""
        account = Account("ACC-002", "checking", balance=500.0)

        assert account.account_number == "ACC-002"
        assert account.account_type == "checking"
        assert account.balance == 500.0

    def test_create_account_with_zero_balance_explicitly(self):
        """Passing balance=0.0 explicitly should work fine."""
        account = Account("ACC-003", "savings", balance=0.0)
        assert account.balance == 0.0

    def test_create_account_invalid_type_raises_error(self):
        """An invalid account type should raise a ValueError."""
        with pytest.raises(ValueError, match="Invalid account type"):
            Account("ACC-004", "premium")

    def test_create_account_negative_balance_raises_error(self):
        """A negative initial balance should raise a ValueError."""
        with pytest.raises(ValueError, match="Initial balance cannot be negative"):
            Account("ACC-005", "savings", balance=-100.0)

    def test_create_account_empty_number_raises_error(self):
        """An empty account number should raise a ValueError."""
        with pytest.raises(ValueError, match="Account number cannot be empty"):
            Account("", "savings")

    def test_create_account_whitespace_number_raises_error(self):
        """A whitespace-only account number should raise a ValueError."""
        with pytest.raises(ValueError, match="Account number cannot be empty"):
            Account("   ", "savings")


# ──────────────────────────────────────────────
#  Deposits
# ──────────────────────────────────────────────


class TestDeposit:
    """Tests for the deposit() method."""

    def test_deposit_increases_balance(self):
        """Depositing money should add to the balance."""
        account = Account("ACC-100", "savings", balance=100.0)
        new_balance = account.deposit(50.0)

        assert new_balance == 150.0
        assert account.get_balance() == 150.0

    def test_deposit_returns_new_balance(self):
        """deposit() should return the updated balance."""
        account = Account("ACC-101", "checking")
        result = account.deposit(200.0)

        assert result == 200.0

    def test_deposit_multiple_times_accumulates(self):
        """Multiple deposits should accumulate correctly."""
        account = Account("ACC-102", "savings")
        account.deposit(100.0)
        account.deposit(50.0)
        account.deposit(25.0)

        assert account.get_balance() == 175.0

    def test_deposit_zero_raises_error(self):
        """Depositing zero should raise a ValueError."""
        account = Account("ACC-103", "savings", balance=100.0)

        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            account.deposit(0)

    def test_deposit_negative_raises_error(self):
        """Depositing a negative amount should raise a ValueError."""
        account = Account("ACC-104", "savings", balance=100.0)

        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            account.deposit(-50.0)


# ──────────────────────────────────────────────
#  Withdrawals
# ──────────────────────────────────────────────


class TestWithdraw:
    """Tests for the withdraw() method."""

    def test_withdraw_decreases_balance(self):
        """Withdrawing money should reduce the balance."""
        account = Account("ACC-200", "checking", balance=500.0)
        new_balance = account.withdraw(200.0)

        assert new_balance == 300.0
        assert account.get_balance() == 300.0

    def test_withdraw_returns_new_balance(self):
        """withdraw() should return the updated balance."""
        account = Account("ACC-201", "savings", balance=1000.0)
        result = account.withdraw(400.0)

        assert result == 600.0

    def test_withdraw_entire_balance(self):
        """Withdrawing the exact balance should leave 0.0."""
        account = Account("ACC-202", "savings", balance=250.0)
        account.withdraw(250.0)

        assert account.get_balance() == 0.0

    def test_withdraw_insufficient_balance_raises_error(self):
        """Withdrawing more than the balance should raise a ValueError."""
        account = Account("ACC-203", "savings", balance=100.0)

        with pytest.raises(ValueError, match="Insufficient balance"):
            account.withdraw(150.0)

    def test_withdraw_zero_raises_error(self):
        """Withdrawing zero should raise a ValueError."""
        account = Account("ACC-204", "checking", balance=100.0)

        with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
            account.withdraw(0)

    def test_withdraw_negative_raises_error(self):
        """Withdrawing a negative amount should raise a ValueError."""
        account = Account("ACC-205", "checking", balance=100.0)

        with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
            account.withdraw(-50.0)

    def test_withdraw_from_zero_balance_raises_error(self):
        """Withdrawing from a zero-balance account should raise a ValueError."""
        account = Account("ACC-206", "savings")

        with pytest.raises(ValueError, match="Insufficient balance"):
            account.withdraw(1.0)


# ──────────────────────────────────────────────
#  get_balance
# ──────────────────────────────────────────────


class TestGetBalance:
    """Tests for the get_balance() method."""

    def test_get_balance_returns_initial_balance(self):
        """get_balance() should return the balance set at creation."""
        account = Account("ACC-300", "savings", balance=750.0)
        assert account.get_balance() == 750.0

    def test_get_balance_reflects_transactions(self):
        """get_balance() should reflect deposits and withdrawals."""
        account = Account("ACC-301", "checking", balance=1000.0)
        account.deposit(500.0)
        account.withdraw(200.0)

        assert account.get_balance() == 1300.0


# ──────────────────────────────────────────────
#  __repr__
# ──────────────────────────────────────────────


class TestRepr:
    """Tests for the __repr__ method."""

    def test_repr_contains_account_info(self):
        """__repr__ should include account number, type, and balance."""
        account = Account("ACC-400", "savings", balance=100.0)
        result = repr(account)

        assert "ACC-400" in result
        assert "savings" in result
        assert "100.0" in result


# ──────────────────────────────────────────────
#  Encapsulation
# ──────────────────────────────────────────────


class TestEncapsulation:
    """Tests verifying that balance is properly encapsulated.

    The balance should be read-only from outside the class.
    Only deposit() and withdraw() may change it.
    """

    def test_balance_is_readable_via_property(self):
        """account.balance should return the current balance (read access)."""
        account = Account("ACC-500", "savings", balance=300.0)
        assert account.balance == 300.0

    def test_balance_cannot_be_set_directly(self):
        """Assigning to account.balance should raise AttributeError."""
        account = Account("ACC-501", "savings", balance=100.0)

        with pytest.raises(AttributeError):
            account.balance = 999.0

        # Balance must remain unchanged
        assert account.balance == 100.0

    def test_balance_property_matches_get_balance(self):
        """The balance property and get_balance() should return the same value."""
        account = Account("ACC-502", "checking", balance=200.0)
        account.deposit(50.0)

        assert account.balance == account.get_balance()
        assert account.balance == 250.0

    def test_balance_only_changes_through_deposit(self):
        """Balance should increase only when deposit() is called."""
        account = Account("ACC-503", "savings")
        assert account.balance == 0.0

        account.deposit(100.0)
        assert account.balance == 100.0

    def test_balance_only_changes_through_withdraw(self):
        """Balance should decrease only when withdraw() is called."""
        account = Account("ACC-504", "savings", balance=500.0)

        account.withdraw(150.0)
        assert account.balance == 350.0

