# FinSight — How to Use the System (Current State)

## 🎯 What You Can Do Now

After completing Phases 5-8, you can:
- ✅ Create users and accounts
- ✅ Deposit and withdraw money
- ✅ Record transactions
- ✅ View transaction history
- ✅ Persist data to PostgreSQL
- ✅ All data survives application restarts!

---

## 🚀 Quick Start

### 1. Setup (One-Time)

```bash
# Navigate to backend
cd C:\Users\Nandesh\Downloads\Finsight\Finsight\backend

# Setup PostgreSQL database
python scripts/setup_database.py
```

### 2. Enter and View Data

**Option A: Interactive CLI** (Easiest)
```bash
python scripts/interactive_cli.py
```

You'll see a menu:
```
1. Create User
2. Create Account
3. Deposit Money
4. Withdraw Money
5. View User
6. View Account
7. View Transaction History
8. List All Users
9. List All Accounts
0. Exit
```

**Option B: Run Example Script**
```bash
python examples/database_example.py
```

This automatically creates sample data and shows you how everything works.

---

## 📝 Common Tasks

### Create a User
```
1. Create User
User ID: USER-001
Name: Alice Johnson
Email: alice@example.com
```

### Create an Account
```
2. Create Account
User ID: USER-001
Account type: savings
Initial balance: 1000
```

### Deposit Money
```
3. Deposit Money
User ID: USER-001
Account number: ACC-000001
Amount: 200
Description: Salary
```

### View Transaction History
```
7. View Transaction History
Account number: ACC-000001
```

---

## 💻 For Developers

### Using Python Code

```python
from app.domain.user import User
from app.repositories import (
    PostgreSQLUserRepository,
    PostgreSQLAccountRepository,
    PostgreSQLTransactionRepository
)
from app.services import AccountService, TransactionService
from app.database import get_db_session, init_database

# Initialize
init_database()
db = next(get_db_session())

# Create repositories
user_repo = PostgreSQLUserRepository(db)
account_repo = PostgreSQLAccountRepository(db)
transaction_repo = PostgreSQLTransactionRepository(db)

# Create services
account_service = AccountService(user_repo, account_repo)
transaction_service = TransactionService(transaction_repo)

# Use the services
user = User("USER-001", "Alice", "alice@example.com")
user_repo.create(user)

account = account_service.create_account(user, "savings", 1000.0)
txn, balance = transaction_service.record_deposit(account, 200.0, "Salary")

# Close session
db.close()
```

---

## 🗄️ Direct Database Access

```bash
# Connect to PostgreSQL
psql -U finsight_user -d finsight_db
```

```sql
-- View all data
SELECT * FROM users;
SELECT * FROM accounts;
SELECT * FROM transactions ORDER BY timestamp DESC;

-- Complex queries
SELECT u.name, a.account_number, a.balance, COUNT(t.transaction_id) as txn_count
FROM users u
JOIN accounts a ON u.user_id = a.user_id
LEFT JOIN transactions t ON a.account_number = t.account_number
GROUP BY u.name, a.account_number, a.balance;
```

---

## 🎯 What's Available

### Domain Models (Business Logic)
- ✅ User — with multiple accounts
- ✅ Account — with balance and transactions
- ✅ Transaction — immutable transaction records

### Services (Operations)
- ✅ AccountService — create accounts, deposits, withdrawals
- ✅ TransactionService — record transactions, view history

### Repositories (Persistence)
- ✅ In-Memory — for testing (fast)
- ✅ PostgreSQL — for production (persistent)

### Tools
- ✅ Interactive CLI — menu-driven interface
- ✅ Example scripts — automated demonstrations
- ✅ Database setup — one-command initialization

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and current status |
| `DATABASE_SETUP.md` | PostgreSQL setup instructions |
| `HOW_TO_USE_DATA.md` | Complete guide to entering/retrieving data |
| `PHASE5_SUMMARY.md` | Domain layer (User, Account, Transaction) |
| `PHASE6_SUMMARY.md` | Service layer (coordination) |
| `PHASE7_SUMMARY.md` | Repository layer (abstraction) |
| `PHASE8_SUMMARY.md` | PostgreSQL + SQLAlchemy integration |

---

## ❓ Common Questions

### Q: Where is the REST API?
**A:** Not implemented yet. Coming in Phase 9 (FastAPI endpoints).

### Q: Can I access data via HTTP?
**A:** Not yet. Currently use Interactive CLI or Python code.

### Q: Does data persist after restart?
**A:** Yes! Data is saved in PostgreSQL and survives restarts.

### Q: Can I use this in production?
**A:** The architecture is production-ready, but you'll need to add:
- Authentication/authorization
- API endpoints (FastAPI)
- Frontend (Angular)
- Proper secrets management
- Database migrations (Alembic)

### Q: How do I reset the database?
**A:** 
```bash
python
>>> from app.database import drop_database, init_database
>>> drop_database()
>>> init_database()
```

### Q: Can I run tests?
**A:** Yes!
```bash
# Domain tests (fast, no database)
python -m pytest tests/test_user.py tests/test_account.py -v

# Repository tests (with database)
python -m pytest tests/test_user_repository.py -v
```

---

## 🎓 Architecture Highlights

### Clean Architecture
```
┌──────────────────────────┐
│   User Interface         │  ← Interactive CLI, Scripts
│   (Not yet: FastAPI)     │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│   Services               │  ← AccountService, TransactionService
│   (Coordination)         │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│   Repositories           │  ← PostgreSQL/InMemory implementations
│   (Data Access)          │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│   Domain Models          │  ← User, Account, Transaction
│   (Business Logic)       │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│   Database               │  ← PostgreSQL
│   (Storage)              │
└──────────────────────────┘
```

### Key Principles Applied
- ✅ **Separation of Concerns** — Clear layer boundaries
- ✅ **Dependency Injection** — Dependencies injected via constructor
- ✅ **Repository Pattern** — Data access abstraction
- ✅ **Service Layer** — Business operations coordination
- ✅ **Domain Models** — Pure business logic, no database concerns
- ✅ **ORM** — SQLAlchemy for database mapping
- ✅ **Single Responsibility** — Each class has one clear purpose

---

## 🔜 Coming Next

**Phase 9: FastAPI REST API**
- HTTP endpoints for all operations
- Request/Response DTOs
- Swagger documentation
- RESTful API design

Then you'll be able to:
```bash
# Create user via API
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER-001", "name": "Alice", "email": "alice@example.com"}'

# Get account balance
curl http://localhost:8000/accounts/ACC-000001/balance
```

---

## 💡 Tips

1. **Start with the Interactive CLI** — easiest way to explore
2. **Run the example script** — see everything working end-to-end
3. **Check the database** — use psql to see persisted data
4. **Read the documentation** — comprehensive guides for each phase
5. **Try Python REPL** — experiment with the services directly

---

**Ready to start?** Run:
```bash
cd backend
python scripts/interactive_cli.py
```

**Questions?** Check `HOW_TO_USE_DATA.md` for detailed instructions!
