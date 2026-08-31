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

**Phase 2 — OOP + Account Domain**: Account domain model with deposit/withdraw operations, full validation, and comprehensive tests.

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

### Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.

- Health check: http://127.0.0.1:8000/health
- Interactive docs: http://127.0.0.1:8000/docs

### Running Tests

```bash
cd backend
pytest
```

## Project Structure

```
FinSight/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # Marks app as a Python package
│   │   ├── main.py            # FastAPI application entry point
│   │   └── domain/            # Core business logic layer
│   │       ├── __init__.py
│   │       └── account/
│   │           ├── __init__.py    # Re-exports Account class
│   │           └── account.py     # Account domain model
│   ├── tests/
│   │   ├── __init__.py        # Marks tests as a Python package
│   │   ├── test_health.py     # Tests for the /health endpoint
│   │   └── test_account.py    # Tests for the Account domain model
│   ├── requirements.txt       # Python dependencies
│   └── pytest.ini             # Pytest configuration
├── frontend/                  # Angular app (coming later)
├── docs/                      # Project documentation
├── .gitignore
└── README.md
```
