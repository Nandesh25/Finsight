"""
FinSight Domain Integration Example

This script demonstrates the User → Account → Transaction domain relationships
and OOP principles in action. It shows how objects collaborate while respecting
encapsulation and single responsibility.

Run this script from the backend directory:
    cd backend
    python -m examples.domain_example
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.user import User
from app.domain.account import Account


def main():
    """Demonstrate domain model relationships and OOP principles."""

    print("=" * 60)
    print("FinSight Domain Model Demo")
    print("=" * 60)
    print()

    # ──────────────────────────────────────────────
    # 1. Create a User
    # ──────────────────────────────────────────────
    print("1. Creating a user...")
    user = User("USER-001", "Alice Johnson", "alice@example.com")
    print(f"   ✓ {user}")
    print()

    # ──────────────────────────────────────────────
    # 2. Add Multiple Accounts (Composition)
    # ──────────────────────────────────────────────
    print("2. Adding accounts to the user (Composition)...")

    savings = Account("ACC-001", "savings", balance=1000.0)
    checking = Account("ACC-002", "checking", balance=500.0)
    emergency = Account("ACC-003", "savings", balance=2000.0)

    user.add_account(savings)
    user.add_account(checking)
    user.add_account(emergency)

    print(f"   ✓ Added 3 accounts")
    print(f"   ✓ User now has {len(user.accounts)} accounts")
    print()

    # ──────────────────────────────────────────────
    # 3. List All Accounts (Association)
    # ──────────────────────────────────────────────
    print("3. Listing all accounts (Association)...")
    for account in user.list_accounts():
        print(f"   - {account}")
    print()

    # ──────────────────────────────────────────────
    # 4. Find Specific Account
    # ──────────────────────────────────────────────
    print("4. Finding specific account...")
    found = user.find_account("ACC-002")
    if found:
        print(f"   ✓ Found: {found}")
    print()

    # ──────────────────────────────────────────────
    # 5. Perform Transactions (Object Collaboration)
    # ──────────────────────────────────────────────
    print("5. Performing transactions (Object Collaboration)...")
    print("   User delegates operations to Account objects:")

    # User finds the account and calls its methods
    checking_account = user.find_account("ACC-002")
    if checking_account:
        print(f"   - Checking balance before: ${checking_account.balance:.2f}")
        checking_account.deposit(200.0)
        print(f"   - After deposit of $200: ${checking_account.balance:.2f}")
        checking_account.withdraw(100.0)
        print(f"   - After withdrawal of $100: ${checking_account.balance:.2f}")
    print()

    # ──────────────────────────────────────────────
    # 6. Calculate Total Balance
    # ──────────────────────────────────────────────
    print("6. Calculating total balance across all accounts...")
    total = user.get_total_balance()
    print(f"   ✓ Total balance: ${total:.2f}")
    print()

    # ──────────────────────────────────────────────
    # 7. Demonstrate Encapsulation
    # ──────────────────────────────────────────────
    print("7. Demonstrating encapsulation...")
    print("   ✗ Attempting to directly set balance (should fail):")
    try:
        savings.balance = 99999.0
    except AttributeError as e:
        print(f"   ✓ Prevented! Balance is read-only via @property")
    print()

    # ──────────────────────────────────────────────
    # 8. Demonstrate Validation
    # ──────────────────────────────────────────────
    print("8. Demonstrating validation...")
    print("   ✗ Attempting overdraft (should fail):")
    try:
        savings_account = user.find_account("ACC-001")
        savings_account.withdraw(50000.0)
    except ValueError as e:
        print(f"   ✓ Prevented! {e}")
    print()

    # ──────────────────────────────────────────────
    # 9. Remove Account
    # ──────────────────────────────────────────────
    print("9. Removing an account...")
    removed = user.remove_account("ACC-003")
    print(f"   ✓ Removed: {removed}")
    print(f"   ✓ User now has {len(user.accounts)} accounts")
    print()

    # ──────────────────────────────────────────────
    # 10. Final State
    # ──────────────────────────────────────────────
    print("10. Final state...")
    print(f"    User: {user}")
    print(f"    Total Balance: ${user.get_total_balance():.2f}")
    print("    Remaining Accounts:")
    for account in user.list_accounts():
        print(f"      - {account}")
    print()

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("OOP Principles Demonstrated:")
    print("  ✓ Composition: User 'has many' Accounts")
    print("  ✓ Association: User manages Account relationships")
    print("  ✓ Encapsulation: Balance is private, accessed via property")
    print("  ✓ Object Collaboration: User delegates to Account")
    print("  ✓ Single Responsibility: Each class has one clear purpose")
    print("  ✓ Validation: Input validation at domain boundaries")
    print()


if __name__ == "__main__":
    main()
