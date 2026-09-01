# FinSight

> AI-powered FinTech enterprise application — built incrementally for learning.

## Tech Stack (Planned)

| Layer     | Technology                     |
|-----------|--------------------------------|
| Backend   | Python + FastAPI               |
| Frontend  | Angular + TypeScript           |
| Database  | PostgreSQL + SQLAlchemy        |
| AI        | LangChain + LangGraph + RAG   |
| Testing   | Pytest + Playwright            |
| DevOps    | Docker + GitHub Actions        |

## Current Status

**Phase 7 — Repository Layer (COMPLETE)** ✅

Introduced the Repository Pattern to separate data access from business logic. Services now use dependency injection with repository abstractions.

### Completed Phases

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 1-4 | Foundation & Setup | ✅ Complete |
| Phase 5 | User, Account & Domain Relationships | ✅ Complete |
| Phase 6 | Service Layer & Dependency Injection | ✅ Complete |
| Phase 7 | Repository Layer | ✅ Complete |

### What's Implemented

**Domain Layer (Phase 5)**
- User domain model with account management
- Account domain model with encapsulation
- Transaction domain model (immutable value object)
- Full validation and business rules

**Service Layer (Phase 6)**
- AccountService for account operations
- TransactionService for transaction management
- Service layer pattern with coordination logic

**Repository Layer (Phase 7)**
- Repository abstractions (interfaces) using ABC
- In-memory implementations for User, Account, Transaction
- Dependency injection in services
- Separation of data access from business logic

### Architecture

```
┌─────────────────────────────────────┐
│    Presentation Layer               │
│    (Future: FastAPI, Angular)       │
└─────────────────────────────────────┘
               ↓
┌─────────────────────────────────────┐
│    Service Layer          Phase 6   │
│    - AccountService                 │
│    - TransactionService             │
└─────────────────────────────────────┘
               ↓
┌─────────────────────────────────────┐
│    Repository Layer      ← Phase 7  │
│    - UserRepository                 │
│    - AccountRepository              │
│    - TransactionRepository          │
└─────────────────────────────────────┘
               ↓
┌─────────────────────────────────────┐
│    Domain Layer           Phase 5   │
│    - User, Account, Transaction     │
└─────────────────────────────────────┘
               ↓
┌─────────────────────────────────────┐
│    Data Storage                     │
│    - In-Memory (Phase 7)            │
│    - PostgreSQL (Phase 8 - Next)    │
└─────────────────────────────────────┘
```

### Test Coverage

- **Domain Tests:** 72 tests (User, Account, Transaction)
- **Service Tests:** 105 tests (AccountService, TransactionService)
- **Repository Tests:** 66 tests (UserRepository, AccountRepository, TransactionRepository)
- **Total:** 243 tests — All passing ✅

## Getting Started

### Prerequisites

- Python 3.10+

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test suite
pytest tests/test_user.py -v
pytest tests/test_account.py -v
pytest tests/test_transaction.py -v
pytest tests/test_account_service.py -v
pytest tests/test_transaction_service.py -v
pytest tests/test_user_repository.py -v
pytest tests/test_account_repository.py -v
pytest tests/test_transaction_repository.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Running Examples

```bash
cd backend

# Domain layer example (Phase 5)
python -m examples.domain_example

# Service layer example (Phase 6)
python -m examples.service_example
```

## Project Structure

```
FinSight/
├── backend/
│   ├── app/
│   │   ├── domain/                    # Phase 5: Domain Layer
│   │   │   ├── user/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user.py           # User domain model
│   │   │   ├── account/
│   │   │   │   ├── __init__.py
│   │   │   │   └── account.py        # Account domain model
│   │   │   └── transaction/
│   │   │       ├── __init__.py
│   │   │       └── transaction.py    # Transaction domain model
│   │   ├── services/                  # Phase 6: Service Layer
│   │   │   ├── __init__.py
│   │   │   ├── account_service.py    # Account operations
│   │   │   └── transaction_service.py # Transaction operations
│   │   └── repositories/              # Phase 7: Repository Layer
│   │       ├── __init__.py
│   │       ├── user_repository.py    # User data access
│   │       ├── account_repository.py # Account data access
│   │       └── transaction_repository.py # Transaction data access
│   ├── tests/
│   │   ├── test_user.py              # 45 tests
│   │   ├── test_account.py           # 27 tests
│   │   ├── test_transaction.py       # 35 tests
│   │   ├── test_account_service.py   # 33 tests
│   │   ├── test_transaction_service.py # 37 tests
│   │   ├── test_user_repository.py   # 20 tests
│   │   ├── test_account_repository.py # 22 tests
│   │   └── test_transaction_repository.py # 24 tests
│   ├── examples/
│   │   ├── domain_example.py         # Domain layer demo
│   │   └── service_example.py        # Service layer demo
│   ├── requirements.txt
│   └── pytest.ini
├── docs/
│   ├── PHASE5_README.md              # User & Account relationships
│   ├── PHASE5_SUMMARY.md
│   ├── PHASE6_README.md              # Service layer guide
│   ├── PHASE6_SUMMARY.md
│   ├── PHASE7_README.md              # Repository layer guide
│   └── PHASE7_SUMMARY.md
├── .gitignore
└── README.md                         # This file
```

## Architecture Concepts Demonstrated

### Phase 5: Domain Layer
- ✅ Composition (User "has many" Accounts)
- ✅ Association (User manages Account relationships)
- ✅ Encapsulation (private state, controlled access)
- ✅ Object Collaboration (User delegates to Account)
- ✅ Single Responsibility Principle
- ✅ Immutability (Transaction as value object)

### Phase 6: Service Layer
- ✅ Service Layer Pattern (coordinate operations)
- ✅ Separation of Concerns (services coordinate, domains enforce rules)
- ✅ Dependency Injection (prepared for repositories)
- ✅ Single Responsibility (each service handles one area)
- ✅ Domain Logic Delegation (services don't duplicate domain rules)

### Phase 7: Repository Layer
- ✅ Repository Pattern (collection-like interface)
- ✅ Abstraction (services depend on interfaces, not implementations)
- ✅ Dependency Injection (repositories injected via constructor)
- ✅ Separation of Concerns (data access isolated from business logic)
- ✅ Loose Coupling (swappable implementations)
- ✅ Open/Closed Principle (open for extension, closed for modification)

## Quick Start Example

```python
from app.domain.user import User
from app.domain.account import Account
from app.repositories import (
    InMemoryUserRepository,
    InMemoryAccountRepository,
    InMemoryTransactionRepository
)
from app.services import AccountService, TransactionService

# Create repositories (Phase 7)
user_repo = InMemoryUserRepository()
account_repo = InMemoryAccountRepository()
transaction_repo = InMemoryTransactionRepository()

# Inject into services (Dependency Injection)
account_service = AccountService(user_repo, account_repo)
transaction_service = TransactionService(transaction_repo)

# Create user (Domain)
user = User("USER-001", "Alice", "alice@example.com")
user_repo.create(user)

# Create account (Service coordinates)
account = account_service.create_account(user, "savings", initial_balance=1000.0)

# Record transaction (Service + Repository)
txn, new_balance = transaction_service.record_deposit(account, 200.0, "Salary")

# Retrieve history (Repository)
transactions = transaction_service.get_transactions(account.account_number)
print(f"Balance: ${account.balance:.2f}")
print(f"Transactions: {len(transactions)}")
```

## Next Phase

**Phase 8: PostgreSQL Database Integration**
- Implement database-backed repositories
- SQLAlchemy ORM models
- Database migrations with Alembic
- Connection pooling
- Transaction management

Services won't need to change because they depend on repository abstractions!

## Documentation

- **PHASE5_README.md** — Complete guide to domain layer
- **PHASE6_README.md** — Complete guide to service layer
- **PHASE7_README.md** — Complete guide to repository layer
- Each phase has detailed documentation and examples

## Contributing

This is a learning project built incrementally to demonstrate enterprise architecture patterns in Python.

## License

MIT
