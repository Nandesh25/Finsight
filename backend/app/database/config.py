"""
FinSight — Database Configuration

This module handles database connection, session management, and configuration.

Key Architecture Concepts:
    - SQLAlchemy Engine: Database connection pool
    - Session Factory: Creates database sessions
    - Environment-based Configuration: Different settings for dev/test/prod
    - Dependency Injection: Sessions provided via dependency injection
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

# Import Base to ensure models are registered
from app.database.models import Base


class DatabaseConfig:
    """
    Database configuration container.

    Supports environment-based configuration through environment variables.
    """

    def __init__(self):
        """Initialize database configuration from environment variables."""
        # Database URL from environment or default to local PostgreSQL
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://finsight_user:finsight_pass@localhost:5432/finsight_db"
        )

        # Test database URL (in-memory SQLite for testing)
        self.test_database_url = os.getenv(
            "TEST_DATABASE_URL",
            "sqlite:///:memory:"
        )

        # Environment (development, testing, production)
        self.environment = os.getenv("ENVIRONMENT", "development")

    def get_database_url(self) -> str:
        """
        Get the appropriate database URL based on environment.

        Returns:
            Database connection string
        """
        if self.environment == "testing":
            return self.test_database_url
        return self.database_url


# Global configuration instance
config = DatabaseConfig()


def create_database_engine(database_url: str = None, echo: bool = False):
    """
    Create a SQLAlchemy engine.

    Args:
        database_url: Database connection string (uses config if None)
        echo: Whether to log SQL statements

    Returns:
        SQLAlchemy Engine instance
    """
    url = database_url or config.get_database_url()

    # Special configuration for SQLite (testing)
    if url.startswith("sqlite"):
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=echo
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            echo=echo
        )

    return engine


def create_session_factory(engine):
    """
    Create a session factory bound to an engine.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        sessionmaker instance
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Global engine and session factory (initialized on module import)
# These can be overridden for testing
engine = create_database_engine()
SessionLocal = create_session_factory(engine)


def init_database():
    """
    Initialize the database by creating all tables.

    This should be called once when setting up the application.
    In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def drop_database():
    """
    Drop all tables from the database.

    WARNING: This deletes all data. Use only for testing or development.
    """
    Base.metadata.drop_all(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency injection function for database sessions.

    Yields a database session and ensures it's closed after use.
    This is designed to be used with FastAPI's Depends() in future phases.

    Usage:
        db = next(get_db_session())
        try:
            # Use db
        finally:
            db.close()

    Yields:
        SQLAlchemy Session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session_for_testing(database_url: str = None):
    """
    Create a database session for testing.

    Args:
        database_url: Optional test database URL

    Returns:
        SQLAlchemy Session instance
    """
    test_engine = create_database_engine(database_url or config.test_database_url)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = create_session_factory(test_engine)
    return TestSessionLocal()
