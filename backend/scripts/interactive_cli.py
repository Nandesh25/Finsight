"""
FinSight — Interactive CLI for Data Entry

This script provides an interactive command-line interface to enter and
retrieve data from the FinSight database.

Run this from the backend directory:
    python scripts/interactive_cli.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.user import User
from app.repositories import (
    PostgreSQLUserRepository,
    PostgreSQLAccountRepository,
    PostgreSQLTransactionRepository
)
from app.services import AccountService, TransactionService
from app.database import get_db_session, init_database


class FinSightCLI:
    """Interactive CLI for FinSight."""

    def __init__(self):
        """Initialize CLI with database session."""
        init_database()
        self.db = next(get_db_session())

        self.user_repo = PostgreSQLUserRepository(self.db)
        self.account_repo = PostgreSQLAccountRepository(self.db)
        self.transaction_repo = PostgreSQLTransactionRepository(self.db)

        self.account_service = AccountService(self.user_repo, self.account_repo)
        self.transaction_service = TransactionService(self.transaction_repo)

    def close(self):
        """Close database session."""
        self.db.close()

    def show_menu(self):
        """Display main menu."""
        print("\n" + "=" * 60)
        print("FinSight Interactive CLI")
        print("=" * 60)
        print("1. Create User")
        print("2. Create Account")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. View User")
        print("6. View Account")
        print("7. View Transaction History")
        print("8. List All Users")
        print("9. List All Accounts")
        print("0. Exit")
        print("=" * 60)

    def create_user(self):
        """Create a new user."""
        print("\n--- Create User ---")
        user_id = input("User ID (e.g., USER-001): ").strip()
        name = input("Name: ").strip()
        email = input("Email: ").strip()

        try:
            user = User(user_id, name, email)
            self.user_repo.create(user)
            print(f"✓ User created: {user}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def create_account(self):
        """Create a new account."""
        print("\n--- Create Account ---")
        user_id = input("User ID: ").strip()
        account_type = input("Account type (savings/checking): ").strip()
        balance = float(input("Initial balance: ").strip())

        try:
            user = self.user_repo.find_by_id(user_id)
            if not user:
                print(f"✗ User {user_id} not found")
                return

            account = self.account_service.create_account(user, account_type, balance)
            print(f"✓ Account created: {account.account_number} - ${account.balance:.2f}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def deposit(self):
        """Deposit money."""
        print("\n--- Deposit Money ---")
        user_id = input("User ID: ").strip()
        account_number = input("Account number: ").strip()
        amount = float(input("Amount: ").strip())
        description = input("Description (optional): ").strip()

        try:
            user = self.user_repo.find_by_id(user_id)
            if not user:
                print(f"✗ User {user_id} not found")
                return

            account = self.account_repo.find_by_account_number(account_number)
            if not account:
                print(f"✗ Account {account_number} not found")
                return

            txn, new_balance = self.transaction_service.record_deposit(
                account, amount, description
            )
            print(f"✓ Deposited ${amount:.2f}")
            print(f"  Transaction ID: {txn.transaction_id}")
            print(f"  New balance: ${new_balance:.2f}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def withdraw(self):
        """Withdraw money."""
        print("\n--- Withdraw Money ---")
        user_id = input("User ID: ").strip()
        account_number = input("Account number: ").strip()
        amount = float(input("Amount: ").strip())
        description = input("Description (optional): ").strip()

        try:
            user = self.user_repo.find_by_id(user_id)
            if not user:
                print(f"✗ User {user_id} not found")
                return

            account = self.account_repo.find_by_account_number(account_number)
            if not account:
                print(f"✗ Account {account_number} not found")
                return

            txn, new_balance = self.transaction_service.record_withdrawal(
                account, amount, description
            )
            print(f"✓ Withdrew ${amount:.2f}")
            print(f"  Transaction ID: {txn.transaction_id}")
            print(f"  New balance: ${new_balance:.2f}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_user(self):
        """View user details."""
        print("\n--- View User ---")
        user_id = input("User ID: ").strip()

        try:
            user = self.user_repo.find_by_id(user_id)
            if not user:
                print(f"✗ User {user_id} not found")
                return

            print(f"\nUser: {user.user_id}")
            print(f"  Name: {user.name}")
            print(f"  Email: {user.email}")
            print(f"  Accounts: {len(user.accounts)}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_account(self):
        """View account details."""
        print("\n--- View Account ---")
        account_number = input("Account number: ").strip()

        try:
            account = self.account_repo.find_by_account_number(account_number)
            if not account:
                print(f"✗ Account {account_number} not found")
                return

            print(f"\nAccount: {account.account_number}")
            print(f"  Type: {account.account_type}")
            print(f"  Balance: ${account.balance:.2f}")

            # Get transaction count
            txn_count = self.transaction_service.get_transaction_count(account_number)
            print(f"  Transactions: {txn_count}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_transactions(self):
        """View transaction history."""
        print("\n--- Transaction History ---")
        account_number = input("Account number: ").strip()

        try:
            transactions = self.transaction_service.get_transactions(account_number)

            if not transactions:
                print(f"No transactions found for account {account_number}")
                return

            print(f"\nTransactions for {account_number}:")
            print("-" * 60)
            for txn in transactions:
                print(f"{txn.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                      f"{txn.transaction_type:11s} | ${txn.amount:8.2f} | "
                      f"{txn.description}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def list_users(self):
        """List all users."""
        print("\n--- All Users ---")
        try:
            users = self.user_repo.list_all()
            if not users:
                print("No users found")
                return

            for user in users:
                print(f"{user.user_id} | {user.name:20s} | {user.email}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def list_accounts(self):
        """List all accounts."""
        print("\n--- All Accounts ---")
        try:
            accounts = self.account_repo.list_all()
            if not accounts:
                print("No accounts found")
                return

            for account in accounts:
                print(f"{account.account_number} | {account.account_type:10s} | ${account.balance:10.2f}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def run(self):
        """Run the interactive CLI."""
        try:
            while True:
                self.show_menu()
                choice = input("\nEnter your choice: ").strip()

                if choice == "1":
                    self.create_user()
                elif choice == "2":
                    self.create_account()
                elif choice == "3":
                    self.deposit()
                elif choice == "4":
                    self.withdraw()
                elif choice == "5":
                    self.view_user()
                elif choice == "6":
                    self.view_account()
                elif choice == "7":
                    self.view_transactions()
                elif choice == "8":
                    self.list_users()
                elif choice == "9":
                    self.list_accounts()
                elif choice == "0":
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")

        finally:
            self.close()


if __name__ == "__main__":
    cli = FinSightCLI()
    cli.run()
