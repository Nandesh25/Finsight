"""
FinSight Database Setup Script

This script initializes the PostgreSQL database and creates all tables.
Run this once before starting the application.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import init_database, engine, Base


def setup_database():
    """
    Initialize the database by creating all tables.
    """
    print("=" * 60)
    print("FinSight Database Setup")
    print("=" * 60)
    print()

    # Check database connection
    try:
        connection = engine.connect()
        print("✓ Successfully connected to database")
        connection.close()
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        print()
        print("Please ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Database 'finsight_db' exists")
        print("3. User 'finsight_user' exists with password 'finsight_pass'")
        print("4. User has permissions on the database")
        print()
        print("See DATABASE_SETUP.md for detailed instructions")
        return False

    # Create tables
    try:
        print("Creating database tables...")
        init_database()
        print("✓ All tables created successfully")
        print()

        # List created tables
        print("Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

        print()
        print("=" * 60)
        print("Database setup complete!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
