"""
Integration example demonstrating the Service Layer with Domain Models.

This script shows how AccountService and TransactionService coordinate
operations across User, Account, and Transaction domain objects.

Run from the backend directory:
    cd backend
    python -m examples.service_example
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.user import User
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService


def main():
    """Demonstrate service layer coordination with domain models."""

    print("=" * 60)
    print("FinSight Service Layer Demo")
    print("=" * 60)
    print()

    # ──────────────────────────────────────────────
    # 1. Initialize Services
    # ──────────────────────────────────────────────
    print("1. Initializing services...")
    account_service = AccountService()
    transaction_service = TransactionService()
    print("   ✓ AccountService initialized")
    print("   ✓ TransactionService initialized")
    print()

    # ──────────────────────────────────────────────
    # 2. Create User
    # ──────────────────────────────────────────────
    print("2. Creating a user...")
    user = User("USER-001", "Alice Johnson", "alice@example.com")
    print(f"   ✓ {user}")
    print()

    # ──────────────────────────────────────────────
    # 3. Create Accounts via Service
    # ──────────────────────────────────────────────
    print("3. Creating accounts via AccountService...")

    savings = account_service.create_account(user, "savings", initial_balance=1000.0)
    checking = account_service.create_account(user, "checking", initial_balance=500.0)

    print(f"   ✓ Created savings account: {savings.account_number} (${savings.balance:.2f})")
    print(f"   ✓ Created checking account: {checking.account_number} (${checking.balance:.2f})")
    print()

    # ──────────────────────────────────────────────
    # 4. Perform Deposit with Transaction Recording
    # ──────────────────────────────────────────────
    print("4. Depositing money with transaction recording...")

    # Use transaction service to record deposit
    txn1, new_balance = transaction_service.record_deposit(
        savings,
        200.0,
        "Monthly salary deposit"
    )
    print(f"   ✓ Deposited $200 to {savings.account_number}")
    print(f"   ✓ New balance: ${new_balance:.2f}")
    print(f"   ✓ Transaction recorded: {txn1.transaction_id}")
    print()

    # ──────────────────────────────────────────────
    # 5. Perform Withdrawal with Transaction Recording
    # ──────────────────────────────────────────────
    print("5. Withdrawing money with transaction recording...")

    txn2, new_balance = transaction_service.record_withdrawal(
        checking,
        100.0,
        "ATM withdrawal"
    )
    print(f"   ✓ Withdrew $100 from {checking.account_number}")
    print(f"   ✓ New balance: ${new_balance:.2f}")
    print(f"   ✓ Transaction recorded: {txn2.transaction_id}")
    print()

    # ──────────────────────────────────────────────
    # 6. Validate Transaction Before Execution
    # ──────────────────────────────────────────────
    print("6. Validating a potential withdrawal...")

    is_valid, error = transaction_service.validate_transaction(
        savings,
        "withdrawal",
        5000.0
    )
    if is_valid:
        print("   ✓ Transaction would be valid")
    else:
        print(f"   ✗ Transaction would fail: {error}")
    print()

    # ──────────────────────────────────────────────
    # 7. List All Accounts via Service
    # ──────────────────────────────────────────────
    print("7. Listing all accounts via AccountService...")
    accounts = account_service.list_accounts(user)
    for account in accounts:
        balance = account_service.get_account_balance(user, account.account_number)
        print(f"   - {account.account_number} ({account.account_type}): ${balance:.2f}")
    print()

    # ──────────────────────────────────────────────
    # 8. View Transaction History
    # ──────────────────────────────────────────────
    print("8. Viewing transaction history...")

    print(f"\n   Transactions for {savings.account_number}:")
    savings_txns = transaction_service.get_transactions(savings.account_number)
    for txn in savings_txns:
        print(f"     - {txn.transaction_id}: {txn.transaction_type} ${txn.amount:.2f}")
        if txn.description:
            print(f"       Description: {txn.description}")

    print(f"\n   Transactions for {checking.account_number}:")
    checking_txns = transaction_service.get_transactions(checking.account_number)
    for txn in checking_txns:
        print(f"     - {txn.transaction_id}: {txn.transaction_type} ${txn.amount:.2f}")
        if txn.description:
            print(f"       Description: {txn.description}")
    print()

    # ──────────────────────────────────────────────
    # 9. Get Transaction Statistics
    # ──────────────────────────────────────────────
    print("9. Transaction statistics...")

    savings_count = transaction_service.get_transaction_count(savings.account_number)
    savings_deposited = transaction_service.get_total_deposited(savings.account_number)
    savings_withdrawn = transaction_service.get_total_withdrawn(savings.account_number)

    print(f"   {savings.account_number}:")
    print(f"     - Total transactions: {savings_count}")
    print(f"     - Total deposited: ${savings_deposited:.2f}")
    print(f"     - Total withdrawn: ${savings_withdrawn:.2f}")
    print()

    # ──────────────────────────────────────────────
    # 10. Close Account (Balance Must Be Zero)
    # ──────────────────────────────────────────────
    print("10. Attempting to close an account...")

    # Try to close savings (has balance - should fail)
    try:
        account_service.close_account(user, savings.account_number)
        print("   ✗ Closed account with balance (should not happen)")
    except ValueError as e:
        print(f"   ✓ Prevented closing account with balance: {e}")
    print()

    # ──────────────────────────────────────────────
    # 11. Final Summary
    # ──────────────────────────────────────────────
    print("11. Final summary...")
    print(f"    User: {user.name}")
    print(f"    Email: {user.email}")
    print(f"    Total accounts: {len(user.accounts)}")
    print(f"    Total balance: ${user.get_total_balance():.2f}")
    print()

    print("=" * 60)
    print("Service Layer Demo Complete!")
    print("=" * 60)
    print()
    print("Architecture Concepts Demonstrated:")
    print("  ✓ Service Layer: Coordinates operations across domain objects")
    print("  ✓ Separation of Concerns: Services coordinate, domains enforce rules")
    print("  ✓ Dependency Injection: Services depend on domain abstractions")
    print("  ✓ Single Responsibility: Each service handles one area")
    print("  ✓ Domain Logic Delegation: Services don't duplicate domain rules")
    print("  ✓ Transaction Recording: Immutable audit trail")
    print()


if __name__ == "__main__":
    main()
