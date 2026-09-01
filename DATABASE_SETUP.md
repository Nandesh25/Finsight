# FinSight Database Setup Guide

This guide walks you through setting up PostgreSQL for the FinSight application.

## Prerequisites

- PostgreSQL 12+ installed
- Python 3.10+ with pip
- SQLAlchemy and psycopg2 installed

## Quick Start

### 1. Install PostgreSQL

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Install Python Dependencies

```bash
cd backend
pip install sqlalchemy psycopg2-binary python-dotenv
```

Or update `requirements.txt`:
```txt
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### 3. Create Database and User

```bash
# Access PostgreSQL as superuser
# Windows (Command Prompt as Admin):
psql -U postgres

# macOS/Linux:
sudo -u postgres psql
```

Then run these SQL commands:

```sql
-- Create database
CREATE DATABASE finsight_db;

-- Create user
CREATE USER finsight_user WITH PASSWORD 'finsight_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE finsight_db TO finsight_user;

-- Connect to the database
\c finsight_db

-- Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO finsight_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO finsight_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO finsight_user;

-- Exit
\q
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://finsight_user:finsight_pass@localhost:5432/finsight_db
ENVIRONMENT=development
```

### 5. Initialize Database Tables

```bash
cd backend
python scripts/setup_database.py
```

Expected output:
```
============================================================
FinSight Database Setup
============================================================

✓ Successfully connected to database
Creating database tables...
✓ All tables created successfully

Created tables:
  - users
  - accounts
  - transactions
  - payments

============================================================
Database setup complete!
============================================================
```

## Database Schema

### Tables

**users**
- `user_id` (VARCHAR(50), PRIMARY KEY)
- `name` (VARCHAR(200), NOT NULL)
- `email` (VARCHAR(200), NOT NULL, UNIQUE)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**accounts**
- `account_number` (VARCHAR(50), PRIMARY KEY)
- `user_id` (VARCHAR(50), FOREIGN KEY → users.user_id)
- `account_type` (ENUM: 'savings', 'checking')
- `balance` (FLOAT, NOT NULL, DEFAULT 0.0)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**transactions**
- `transaction_id` (VARCHAR(50), PRIMARY KEY)
- `account_number` (VARCHAR(50), FOREIGN KEY → accounts.account_number)
- `transaction_type` (ENUM: 'deposit', 'withdrawal')
- `amount` (FLOAT, NOT NULL)
- `description` (VARCHAR(500))
- `timestamp` (TIMESTAMP)
- `created_at` (TIMESTAMP)

**payments** (prepared for future use)
- `payment_id` (VARCHAR(50), PRIMARY KEY)
- `from_account` (VARCHAR(50), FOREIGN KEY → accounts.account_number)
- `to_account` (VARCHAR(50), FOREIGN KEY → accounts.account_number)
- `amount` (FLOAT, NOT NULL)
- `description` (VARCHAR(500))
- `status` (VARCHAR(50), DEFAULT 'pending')
- `timestamp` (TIMESTAMP)
- `created_at` (TIMESTAMP)

### Relationships

```
User (1) ─────→ (N) Account
                      │
                      └────→ (N) Transaction
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://finsight_user:finsight_pass@localhost:5432/finsight_db` |
| `TEST_DATABASE_URL` | Test database (SQLite) | `sqlite:///:memory:` |
| `ENVIRONMENT` | Environment (development/testing/production) | `development` |

### Connection String Format

```
postgresql://username:password@host:port/database_name
```

Examples:
```bash
# Local development
DATABASE_URL=postgresql://finsight_user:finsight_pass@localhost:5432/finsight_db

# Docker
DATABASE_URL=postgresql://finsight_user:finsight_pass@db:5432/finsight_db

# Cloud (Heroku, Railway, etc.)
DATABASE_URL=postgresql://user:pass@host.com:5432/dbname
```

## Verifying the Setup

### 1. Check Database Connection

```bash
cd backend
python -c "from app.database import engine; print('✓ Database connection successful' if engine.connect() else '✗ Connection failed')"
```

### 2. Check Tables

```bash
psql -U finsight_user -d finsight_db -c "\dt"
```

Expected output:
```
             List of relations
 Schema |     Name     | Type  |     Owner
--------+--------------+-------+---------------
 public | accounts     | table | finsight_user
 public | payments     | table | finsight_user
 public | transactions | table | finsight_user
 public | users        | table | finsight_user
```

### 3. Run Tests

```bash
cd backend
python -m pytest tests/test_user_repository.py -v
```

## Using PostgreSQL Repositories

### Example: Create User with Database

```python
from app.domain.user import User
from app.repositories import PostgreSQLUserRepository
from app.database import get_db_session

# Get database session
db = next(get_db_session())

try:
    # Create repository with session
    user_repo = PostgreSQLUserRepository(db)
    
    # Create user
    user = User("USER-001", "Alice", "alice@example.com")
    user_repo.create(user)
    
    # Find user
    found = user_repo.find_by_id("USER-001")
    print(f"Found: {found.name}")
    
finally:
    db.close()
```

### Example: Services with PostgreSQL

```python
from app.repositories import (
    PostgreSQLUserRepository,
    PostgreSQLAccountRepository,
    PostgreSQLTransactionRepository
)
from app.services import AccountService, TransactionService
from app.database import get_db_session

# Get database session
db = next(get_db_session())

try:
    # Create PostgreSQL repositories
    user_repo = PostgreSQLUserRepository(db)
    account_repo = PostgreSQLAccountRepository(db)
    transaction_repo = PostgreSQLTransactionRepository(db)
    
    # Inject into services (same as before!)
    account_service = AccountService(user_repo, account_repo)
    transaction_service = TransactionService(transaction_repo)
    
    # Services work exactly the same!
    # The abstraction means no service code changes
    
finally:
    db.close()
```

## Troubleshooting

### Connection Refused

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   # Windows
   pg_ctl status
   
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Start PostgreSQL if needed:
   ```bash
   # Windows
   pg_ctl start
   
   # macOS
   brew services start postgresql
   
   # Linux
   sudo systemctl start postgresql
   ```

### Authentication Failed

```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solution:**
1. Verify username and password in `DATABASE_URL`
2. Reset password if needed:
   ```sql
   ALTER USER finsight_user WITH PASSWORD 'new_password';
   ```

### Permission Denied

```
psycopg2.ProgrammingError: permission denied for schema public
```

**Solution:**
```sql
\c finsight_db
GRANT ALL ON SCHEMA public TO finsight_user;
```

### Database Does Not Exist

```
psycopg2.OperationalError: FATAL: database "finsight_db" does not exist
```

**Solution:**
```bash
createdb -U postgres finsight_db
```

Or via psql:
```sql
CREATE DATABASE finsight_db;
```

## Resetting the Database

### Drop and Recreate

```bash
# Connect to PostgreSQL
psql -U postgres

# Drop database
DROP DATABASE IF EXISTS finsight_db;

# Recreate
CREATE DATABASE finsight_db;
GRANT ALL PRIVILEGES ON DATABASE finsight_db TO finsight_user;

# Exit and reinitialize
\q
python scripts/setup_database.py
```

### Clear All Data (Keep Structure)

```python
from app.database import SessionLocal, drop_database, init_database

# Drop all tables
drop_database()

# Recreate tables
init_database()
```

## Production Considerations

### Connection Pooling

SQLAlchemy's connection pool is configured in `app/database/config.py`:

```python
engine = create_engine(
    database_url,
    pool_size=5,          # Number of connections to keep open
    max_overflow=10,      # Additional connections during peak
    pool_pre_ping=True    # Check connections before use
)
```

### Migrations (Future)

For production, use Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Backups

```bash
# Backup database
pg_dump -U finsight_user finsight_db > backup.sql

# Restore database
psql -U finsight_user finsight_db < backup.sql
```

## Next Steps

1. ✅ Database setup complete
2. Run tests with PostgreSQL repositories
3. Try the example scripts with database persistence
4. (Future) Add FastAPI endpoints that use database
5. (Future) Set up Alembic migrations

---

**Questions?** See `PHASE8_README.md` for more details on the PostgreSQL implementation.
