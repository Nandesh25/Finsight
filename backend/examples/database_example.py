"""
FinSight — Interactive Data Entry Example

This script demonstrates how to create, store, and retrieve data using
the PostgreSQL-backed repositories.

Run this from the backend directory:
    python examples/database_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.user import User
from app.domain.account import Account
from app.repositories import (
    PostgreSQLUserRepository,
    PostgreSQLAccountRepository,
    PostgreSQLTransactionRepository
)
from app.services import AccountService, TransactionService
from app.database import get_db_session, init_database


def main():
    """Demonstrate database operations."""

    print("=" * 60)
    print("FinSight Database Example")
    print("=" * 60)
    print()

    # Initialize database (creates tables if they don't exist)
    print("Initializing database...")
    init_database()
    print("✓ Database initialized")
    print()

    # Get database session
    db = next(get_db_session())

    try:
        # Create repositories with database session
        user_repo = PostgreSQLUserRepository(db)
        account_repo = PostgreSQLAccountRepository(db)
        transaction_repo = PostgreSQLTransactionRepository(db)

        # Create services with repositories
        account_service = AccountService(user_repo, account_repo)
        transaction_service = TransactionService(transaction_repo)

        # ──────────────────────────────────────────────
        # 1. Create a User
        # ──────────────────────────────────────────────
        print("1. Creating user...")
        user = User("USER-001", "Alice Johnson", "alice@example.com")
        user_repo.create(user)
        print(f"   ✓ Created: {user}")
        print()

        # ──────────────────────────────────────────────
        # 2. Create Accounts
        # ──────────────────────────────────────────────
        print("2. Creating accounts...")
        savings = account_service.create_account(user, "savings", initial_balance=1000.0)
        checking = account_service.create_account(user, "checking", initial_balance=500.0)
        print(f"   ✓ Savings: {savings.account_number} - ${savings.balance:.2f}")
        print(f"   ✓ Checking: {checking.account_number} - ${checking.balance:.2f}")
        print()

        # ──────────────────────────────────────────────
        # 3. Perform Transactions
        # ──────────────────────────────────────────────
        print("3. Recording transactions...")

        # Deposit to savings
        txn1, balance1 = transaction_service.record_deposit(
            savings, 200.0, "Monthly salary"
        )
        print(f"   ✓ Deposited $200 to savings")
        print(f"     New balance: ${balance1:.2f}")

        # Withdraw from checking
        txn2, balance2 = transaction_service.record_withdrawal(
            checking, 100.0, "ATM withdrawal"
        )
        print(f"   ✓ Withdrew $100 from checking")
        print(f"     New balance: ${balance2:.2f}")
        print()

        # ──────────────────────────────────────────────
        # 4. Retrieve Data
        # ──────────────────────────────────────────────
        print("4. Retrieving data from database...")

        # Find user
        found_user = user_repo.find_by_id("USER-001")
        print(f"   User: {found_user.name} ({found_user.email})")

        # Find account
        found_account = account_repo.find_by_account_number(savings.account_number)
        print(f"   Account: {found_account.account_number} - ${found_account.balance:.2f}")

        # Get transaction history
        transactions = transaction_service.get_transactions(savings.account_number)
        print(f"   Transactions: {len(transactions)}")
        for txn in transactions:
            print(f"     - {txn.transaction_type}: ${txn.amount:.2f} ({txn.description})")
        print()

        # ──────────────────────────────────────────────
        # 5. Statistics
        # ──────────────────────────────────────────────
        print("5. Statistics...")
        all_users = user_repo.list_all()
        all_accounts = account_repo.list_all()
        all_transactions = transaction_repo.list_all()

        print(f"   Total users: {len(all_users)}")
        print(f"   Total accounts: {len(all_accounts)}")
        print(f"   Total transactions: {len(all_transactions)}")
        print()

        print("=" * 60)
        print("✓ Example complete!")
        print("=" * 60)
        print()
        print("The data has been saved to PostgreSQL.")
        print("Run this script again to see the persisted data.")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
