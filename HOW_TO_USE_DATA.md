# How to Enter and Retrieve Data in FinSight

There are currently **3 ways** to work with data in FinSight (before FastAPI endpoints are added):

---

## Method 1: Interactive CLI (Easiest) ⭐

Run the interactive menu-driven CLI:

```bash
cd backend
python scripts/interactive_cli.py
```

This gives you a menu to:
1. Create users
2. Create accounts  
3. Deposit money
4. Withdraw money
5. View users
6. View accounts
7. View transaction history
8. List all users
9. List all accounts

**Example session:**
```
============================================================
FinSight Interactive CLI
============================================================
1. Create User
2. Create Account
...
============================================================

Enter your choice: 1

--- Create User ---
User ID (e.g., USER-001): USER-001
Name: Alice Johnson
Email: alice@example.com
✓ User created: User('USER-001', name='Alice Johnson', ...)
```

---

## Method 2: Python Script (Automated)

Run the example script that creates sample data:

```bash
cd backend
python examples/database_example.py
```

This automatically:
- Creates a user
- Creates 2 accounts (savings & checking)
- Performs transactions
- Displays the data
- Saves everything to PostgreSQL

Run it multiple times to see data persistence!

---

## Method 3: Python REPL (For Testing)

```bash
cd backend
python
```

Then enter this code:

```python
from app.domain.user import User
from app.repositories import (
    PostgreSQLUserRepository,
    PostgreSQLAccountRepository,
    PostgreSQLTransactionRepository
)
from app.services import AccountService, TransactionService
from app.database import get_db_session, init_database

# Initialize database
init_database()

# Get database session
db = next(get_db_session())

# Create repositories
user_repo = PostgreSQLUserRepository(db)
account_repo = PostgreSQLAccountRepository(db)
transaction_repo = PostgreSQLTransactionRepository(db)

# Create services
account_service = AccountService(user_repo, account_repo)
transaction_service = TransactionService(transaction_repo)

# Create a user
user = User("USER-001", "Alice", "alice@example.com")
user_repo.create(user)

# Create an account
account = account_service.create_account(user, "savings", initial_balance=1000.0)
print(f"Created account: {account.account_number}")

# Deposit money
txn, balance = transaction_service.record_deposit(account, 200.0, "Salary")
print(f"New balance: ${balance:.2f}")

# Retrieve data
found_user = user_repo.find_by_id("USER-001")
print(f"Found user: {found_user.name}")

# View transactions
transactions = transaction_service.get_transactions(account.account_number)
print(f"Transactions: {len(transactions)}")
for txn in transactions:
    print(f"  {txn.transaction_type}: ${txn.amount:.2f}")

# Close session when done
db.close()
```

---

## Method 4: Direct SQL (PostgreSQL)

You can also query the database directly:

```bash
# Connect to PostgreSQL
psql -U finsight_user -d finsight_db
```

```sql
-- View all users
SELECT * FROM users;

-- View all accounts
SELECT * FROM accounts;

-- View all transactions
SELECT * FROM transactions ORDER BY timestamp DESC;

-- View user with their accounts
SELECT u.name, a.account_number, a.account_type, a.balance
FROM users u
JOIN accounts a ON u.user_id = a.user_id;

-- View account with transactions
SELECT a.account_number, a.balance, t.transaction_type, t.amount, t.timestamp
FROM accounts a
LEFT JOIN transactions t ON a.account_number = t.account_number
ORDER BY t.timestamp DESC;
```

---

## Quick Start: Step-by-Step

### 1. Setup Database (One-time)

```bash
# Start PostgreSQL (if not running)
# Windows: Services → PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database and user
psql -U postgres
```

```sql
CREATE DATABASE finsight_db;
CREATE USER finsight_user WITH PASSWORD 'finsight_pass';
GRANT ALL PRIVILEGES ON DATABASE finsight_db TO finsight_user;
\q
```

```bash
# Initialize tables
cd backend
python scripts/setup_database.py
```

### 2. Enter Data (Choose one method)

**Option A: Interactive CLI** (Recommended for manual testing)
```bash
python scripts/interactive_cli.py
```

**Option B: Run example script** (Quick demo)
```bash
python examples/database_example.py
```

**Option C: Python REPL** (For custom testing)
```bash
python
# Then paste the code from Method 3 above
```

### 3. Retrieve Data

**In CLI:**
- Choose option 5-9 to view data

**In Python:**
```python
# Get a user
user = user_repo.find_by_id("USER-001")

# Get an account
account = account_repo.find_by_account_number("ACC-000001")

# Get transactions
transactions = transaction_service.get_transactions("ACC-000001")

# List all
all_users = user_repo.list_all()
all_accounts = account_repo.list_all()
```

**In SQL:**
```sql
SELECT * FROM users;
SELECT * FROM accounts;
SELECT * FROM transactions;
```

---

## Common Operations

### Create a User
```python
user = User("USER-002", "Bob Smith", "bob@example.com")
user_repo.create(user)
```

### Create an Account
```python
account = account_service.create_account(user, "checking", 500.0)
```

### Deposit Money
```python
txn, new_balance = transaction_service.record_deposit(account, 100.0, "Deposit")
```

### Withdraw Money
```python
txn, new_balance = transaction_service.record_withdrawal(account, 50.0, "ATM")
```

### Check Balance
```python
balance = account.balance
# or
balance = account_service.get_account_balance(user, account.account_number)
```

### View Transaction History
```python
# All transactions
transactions = transaction_service.get_transactions(account.account_number)

# Only deposits
deposits = transaction_service.get_transactions(account.account_number, transaction_type="deposit")

# Last 10 transactions
recent = transaction_service.get_transactions(account.account_number, limit=10)
```

### Get Statistics
```python
# Total deposited
total_deposited = transaction_service.get_total_deposited(account.account_number)

# Total withdrawn
total_withdrawn = transaction_service.get_total_withdrawn(account.account_number)

# Transaction count
count = transaction_service.get_transaction_count(account.account_number)
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
**Solution:** Run commands from the `backend` directory:
```bash
cd C:\Users\Nandesh\Downloads\Finsight\Finsight\backend
python scripts/interactive_cli.py
```

### "psycopg2.OperationalError: could not connect"
**Solution:** 
1. Make sure PostgreSQL is running
2. Check DATABASE_URL in `.env` file
3. Run `python scripts/setup_database.py`

### "sqlalchemy.exc.OperationalError: no such table"
**Solution:** Initialize database:
```bash
cd backend
python scripts/setup_database.py
```

### Data not persisting
**Solution:** Make sure you're using PostgreSQL repositories, not in-memory:
```python
# ✓ Correct (PostgreSQL)
from app.repositories import PostgreSQLUserRepository
user_repo = PostgreSQLUserRepository(db)

# ✗ Wrong (In-memory, doesn't persist)
from app.repositories import InMemoryUserRepository
user_repo = InMemoryUserRepository()
```

---

## Next Steps

Once FastAPI endpoints are added in the next phase, you'll be able to:
- Use Postman or curl to send HTTP requests
- Access data via REST API endpoints
- Use the Swagger UI at http://localhost:8000/docs

But for now, use the Interactive CLI or Python scripts!

---

## Quick Reference

| Task | Command |
|------|---------|
| Interactive CLI | `python scripts/interactive_cli.py` |
| Run example | `python examples/database_example.py` |
| Python REPL | `python` then import modules |
| SQL console | `psql -U finsight_user -d finsight_db` |
| Setup database | `python scripts/setup_database.py` |
| View tables | `psql -U finsight_user -d finsight_db -c "\dt"` |

---

**Need help?** Check `DATABASE_SETUP.md` for detailed database setup instructions.
