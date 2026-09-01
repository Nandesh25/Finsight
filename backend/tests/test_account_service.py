"""
Tests for the AccountService (Updated for Repository Pattern).

These tests verify that AccountService correctly coordinates operations
between User and Account domain objects using repositories, without
duplicating business logic.

Updated in Phase 7: Now uses repository injection.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest

from app.domain.user import User
from app.domain.account import Account
from app.services.account_service import AccountService
from app.repositories.user_repository import InMemoryUserRepository
from app.repositories.account_repository import InMemoryAccountRepository


# ──────────────────────────────────────────────
#  Account Creation
# ──────────────────────────────────────────────


class TestCreateAccount:
    """Tests for the create_account() method."""

    def test_create_savings_account(self):
        """Creating a savings account should create and add it to the user."""
        user_repo = InMemoryUserRepository()
        account_repo = InMemoryAccountRepository()
        service = AccountService(user_repo, account_repo)
        user = User("USER-001", "Alice", "alice@example.com")

        account = service.create_account(user, "savings", initial_balance=100.0)

        assert account.account_type == "savings"
        assert account.balance == 100.0
        assert len(user.accounts) == 1
        assert user.find_account(account.account_number) is account

    def test_create_checking_account(self):
        """Creating a checking account should create and add it to the user."""
        user_repo = InMemoryUserRepository()
        account_repo = InMemoryAccountRepository()
        service = AccountService(user_repo, account_repo)
        user = User("USER-002", "Bob", "bob@example.com")

        account = service.create_account(user, "checking", initial_balance=500.0)

        assert account.account_type == "checking"
        assert account.balance == 500.0

    def test_create_account_default_balance(self):
        """Creating an account without initial_balance should default to 0.0."""
        user_repo = InMemoryUserRepository()
        account_repo = InMemoryAccountRepository()
        service = AccountService(user_repo, account_repo)
        user = User("USER-003", "Carol", "carol@example.com")

        account = service.create_account(user, "savings")

        assert account.balance == 0.0

    def test_create_account_generates_unique_numbers(self):
        """Each created account should have a unique account number."""
        service = AccountService()
        user = User("USER-004", "Dave", "dave@example.com")

        account1 = service.create_account(user, "savings")
        account2 = service.create_account(user, "checking")

        assert account1.account_number != account2.account_number

    def test_create_multiple_accounts_for_user(self):
        """A user can have multiple accounts created via the service."""
        service = AccountService()
        user = User("USER-005", "Eve", "eve@example.com")

        account1 = service.create_account(user, "savings", 100.0)
        account2 = service.create_account(user, "checking", 200.0)
        account3 = service.create_account(user, "savings", 300.0)

        assert len(user.accounts) == 3

    def test_create_account_invalid_type_raises_error(self):
        """Creating an account with invalid type should raise ValueError."""
        service = AccountService()
        user = User("USER-006", "Frank", "frank@example.com")

        with pytest.raises(ValueError, match="Invalid account type"):
            service.create_account(user, "premium", 100.0)

    def test_create_account_negative_balance_raises_error(self):
        """Creating an account with negative balance should raise ValueError."""
        service = AccountService()
        user = User("USER-007", "Grace", "grace@example.com")

        with pytest.raises(ValueError, match="Initial balance cannot be negative"):
            service.create_account(user, "savings", -100.0)


# ──────────────────────────────────────────────
#  Deposit Operations
# ──────────────────────────────────────────────


class TestDeposit:
    """Tests for the deposit() method."""

    def test_deposit_increases_balance(self):
        """Depositing money should increase the account balance."""
        service = AccountService()
        user = User("USER-100", "Helen", "helen@example.com")
        account = service.create_account(user, "savings", 100.0)

        new_balance = service.deposit(user, account.account_number, 50.0)

        assert new_balance == 150.0
        assert account.balance == 150.0

    def test_deposit_returns_new_balance(self):
        """deposit() should return the updated balance."""
        service = AccountService()
        user = User("USER-101", "Ivan", "ivan@example.com")
        account = service.create_account(user, "checking", 200.0)

        result = service.deposit(user, account.account_number, 100.0)

        assert result == 300.0

    def test_deposit_to_nonexistent_account_raises_error(self):
        """Depositing to a nonexistent account should raise ValueError."""
        service = AccountService()
        user = User("USER-102", "Jane", "jane@example.com")

        with pytest.raises(ValueError, match="Account .* not found"):
            service.deposit(user, "ACC-999999", 100.0)

    def test_deposit_zero_raises_error(self):
        """Depositing zero should raise ValueError (delegated to Account)."""
        service = AccountService()
        user = User("USER-103", "Karl", "karl@example.com")
        account = service.create_account(user, "savings", 100.0)

        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            service.deposit(user, account.account_number, 0.0)

    def test_deposit_negative_raises_error(self):
        """Depositing a negative amount should raise ValueError."""
        service = AccountService()
        user = User("USER-104", "Laura", "laura@example.com")
        account = service.create_account(user, "savings", 100.0)

        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            service.deposit(user, account.account_number, -50.0)


# ──────────────────────────────────────────────
#  Withdrawal Operations
# ──────────────────────────────────────────────


class TestWithdraw:
    """Tests for the withdraw() method."""

    def test_withdraw_decreases_balance(self):
        """Withdrawing money should decrease the account balance."""
        service = AccountService()
        user = User("USER-200", "Mike", "mike@example.com")
        account = service.create_account(user, "checking", 500.0)

        new_balance = service.withdraw(user, account.account_number, 200.0)

        assert new_balance == 300.0
        assert account.balance == 300.0

    def test_withdraw_returns_new_balance(self):
        """withdraw() should return the updated balance."""
        service = AccountService()
        user = User("USER-201", "Nina", "nina@example.com")
        account = service.create_account(user, "savings", 1000.0)

        result = service.withdraw(user, account.account_number, 400.0)

        assert result == 600.0

    def test_withdraw_from_nonexistent_account_raises_error(self):
        """Withdrawing from a nonexistent account should raise ValueError."""
        service = AccountService()
        user = User("USER-202", "Oscar", "oscar@example.com")

        with pytest.raises(ValueError, match="Account .* not found"):
            service.withdraw(user, "ACC-999999", 100.0)

    def test_withdraw_insufficient_balance_raises_error(self):
        """Withdrawing more than balance should raise ValueError (delegated to Account)."""
        service = AccountService()
        user = User("USER-203", "Paula", "paula@example.com")
        account = service.create_account(user, "savings", 100.0)

        with pytest.raises(ValueError, match="Insufficient balance"):
            service.withdraw(user, account.account_number, 200.0)

    def test_withdraw_zero_raises_error(self):
        """Withdrawing zero should raise ValueError."""
        service = AccountService()
        user = User("USER-204", "Quinn", "quinn@example.com")
        account = service.create_account(user, "savings", 100.0)

        with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
            service.withdraw(user, account.account_number, 0.0)

    def test_withdraw_negative_raises_error(self):
        """Withdrawing a negative amount should raise ValueError."""
        service = AccountService()
        user = User("USER-205", "Rachel", "rachel@example.com")
        account = service.create_account(user, "savings", 100.0)

        with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
            service.withdraw(user, account.account_number, -50.0)


# ──────────────────────────────────────────────
#  Get Balance
# ──────────────────────────────────────────────


class TestGetAccountBalance:
    """Tests for the get_account_balance() method."""

    def test_get_balance_returns_current_balance(self):
        """get_account_balance() should return the current balance."""
        service = AccountService()
        user = User("USER-300", "Steve", "steve@example.com")
        account = service.create_account(user, "savings", 750.0)

        balance = service.get_account_balance(user, account.account_number)

        assert balance == 750.0

    def test_get_balance_reflects_transactions(self):
        """get_account_balance() should reflect deposits and withdrawals."""
        service = AccountService()
        user = User("USER-301", "Tina", "tina@example.com")
        account = service.create_account(user, "checking", 1000.0)

        service.deposit(user, account.account_number, 500.0)
        service.withdraw(user, account.account_number, 200.0)

        balance = service.get_account_balance(user, account.account_number)
        assert balance == 1300.0

    def test_get_balance_nonexistent_account_raises_error(self):
        """Getting balance of nonexistent account should raise ValueError."""
        service = AccountService()
        user = User("USER-302", "Uma", "uma@example.com")

        with pytest.raises(ValueError, match="Account .* not found"):
            service.get_account_balance(user, "ACC-999999")


# ──────────────────────────────────────────────
#  Get and List Accounts
# ──────────────────────────────────────────────


class TestGetAndListAccounts:
    """Tests for get_account() and list_accounts() methods."""

    def test_get_account_returns_account(self):
        """get_account() should return the account if it exists."""
        service = AccountService()
        user = User("USER-400", "Victor", "victor@example.com")
        account = service.create_account(user, "savings", 100.0)

        found = service.get_account(user, account.account_number)

        assert found is account

    def test_get_account_returns_none_if_not_found(self):
        """get_account() should return None if account doesn't exist."""
        service = AccountService()
        user = User("USER-401", "Wendy", "wendy@example.com")

        found = service.get_account(user, "ACC-999999")

        assert found is None

    def test_list_accounts_returns_all_accounts(self):
        """list_accounts() should return all accounts for the user."""
        service = AccountService()
        user = User("USER-402", "Xavier", "xavier@example.com")

        account1 = service.create_account(user, "savings", 100.0)
        account2 = service.create_account(user, "checking", 200.0)

        accounts = service.list_accounts(user)

        assert len(accounts) == 2
        assert account1 in accounts
        assert account2 in accounts

    def test_list_accounts_empty_user(self):
        """list_accounts() should return empty list for user with no accounts."""
        service = AccountService()
        user = User("USER-403", "Yara", "yara@example.com")

        accounts = service.list_accounts(user)

        assert accounts == []


# ──────────────────────────────────────────────
#  Close Account
# ──────────────────────────────────────────────


class TestCloseAccount:
    """Tests for the close_account() method."""

    def test_close_account_with_zero_balance(self):
        """Closing an account with zero balance should succeed."""
        service = AccountService()
        user = User("USER-500", "Zack", "zack@example.com")
        account = service.create_account(user, "savings", 0.0)

        closed = service.close_account(user, account.account_number)

        assert closed is account
        assert len(user.accounts) == 0

    def test_close_account_with_nonzero_balance_raises_error(self):
        """Closing an account with balance should raise ValueError."""
        service = AccountService()
        user = User("USER-501", "Amy", "amy@example.com")
        account = service.create_account(user, "savings", 100.0)

        with pytest.raises(ValueError, match="Cannot close account .* with non-zero balance"):
            service.close_account(user, account.account_number)

    def test_close_nonexistent_account_raises_error(self):
        """Closing a nonexistent account should raise ValueError."""
        service = AccountService()
        user = User("USER-502", "Ben", "ben@example.com")

        with pytest.raises(ValueError, match="No account found"):
            service.close_account(user, "ACC-999999")


# ──────────────────────────────────────────────
#  Service Independence
# ──────────────────────────────────────────────


class TestServiceIndependence:
    """Tests verifying service layer doesn't duplicate domain logic."""

    def test_service_delegates_validation_to_domain(self):
        """Service should delegate validation to domain objects, not duplicate it."""
        service = AccountService()
        user = User("USER-600", "Clara", "clara@example.com")

        # Account validation happens in Account.__init__, not in service
        with pytest.raises(ValueError, match="Invalid account type"):
            service.create_account(user, "invalid_type", 100.0)

    def test_service_delegates_balance_rules_to_account(self):
        """Service should delegate balance rules to Account, not duplicate them."""
        service = AccountService()
        user = User("USER-601", "Dan", "dan@example.com")
        account = service.create_account(user, "savings", 50.0)

        # Insufficient balance check happens in Account.withdraw, not in service
        with pytest.raises(ValueError, match="Insufficient balance"):
            service.withdraw(user, account.account_number, 100.0)

    def test_multiple_service_instances_have_independent_counters(self):
        """Different service instances should have independent ID counters."""
        service1 = AccountService()
        service2 = AccountService()

        user1 = User("USER-602", "Ella", "ella@example.com")
        user2 = User("USER-603", "Finn", "finn@example.com")

        account1 = service1.create_account(user1, "savings")
        account2 = service2.create_account(user2, "savings")

        # Both start from counter 1, so both get ACC-000001
        assert account1.account_number == "ACC-000001"
        assert account2.account_number == "ACC-000001"
