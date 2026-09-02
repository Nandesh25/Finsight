"""
FinSight — Authentication Tests

Comprehensive tests for authentication and authorization functionality.

Tests cover:
    - User registration
    - User login
    - Invalid credentials
    - Protected endpoints
    - Role-based access control
    - JWT token validation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.models import Base
from app.database.config import get_db_session
from app.auth.utils import create_access_token


# Setup test database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db_session] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_new_user_success(self):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
        assert data["role"] == "USER"

    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails."""
        # Register first user
        client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        # Try to register with same email
        response = client.post(
            "/auth/register",
            json={
                "name": "Jane Doe",
                "email": "john@example.com",
                "password": "differentpass"
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_invalid_email(self):
        """Test registration with invalid email format fails."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "not-an-email",
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_register_short_password(self):
        """Test registration with too short password fails."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "short"
            }
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_register_missing_fields(self):
        """Test registration with missing required fields fails."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe"
                # Missing email and password
            }
        )

        assert response.status_code == 422


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self):
        """Test successful login with valid credentials."""
        # First register a user
        client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        # Now login
        response = client.post(
            "/auth/login",
            json={
                "email": "john@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "USER"

    def test_login_wrong_password(self):
        """Test login with wrong password fails."""
        # Register a user
        client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "correctpassword"
            }
        )

        # Try to login with wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": "john@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self):
        """Test login with non-existent email fails."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_invalid_email_format(self):
        """Test login with invalid email format fails."""
        response = client.post(
            "/auth/login",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )

        assert response.status_code == 422


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication."""

    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token."""
        # Register and get token
        register_response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )
        token = register_response.json()["access_token"]

        # Access protected endpoint
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "john@example.com"
        assert data["name"] == "John Doe"
        assert data["role"] == "USER"

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token fails."""
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_access_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token fails."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == 401

    def test_access_protected_endpoint_with_expired_token(self):
        """Test accessing protected endpoint with expired token fails."""
        from datetime import timedelta

        # Create an expired token
        expired_token = create_access_token(
            data={"sub": "USER-000001"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401


class TestPasswordSecurity:
    """Tests for password hashing and security."""

    def test_password_not_stored_plaintext(self):
        """Test that passwords are hashed, not stored as plain text."""
        from app.database.config import get_db_session
        from app.database.models import UserModel

        # Register a user
        client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "mypassword123"
            }
        )

        # Check database directly
        db = next(override_get_db())
        user = db.query(UserModel).filter_by(email="john@example.com").first()

        # Password should be hashed, not plain text
        assert user.hashed_password != "mypassword123"
        assert len(user.hashed_password) > 50  # Bcrypt hashes are long
        assert user.hashed_password.startswith("$2b$")  # Bcrypt format

    def test_same_password_different_hashes(self):
        """Test that same password gets different hashes (salt)."""
        # Register two users with same password
        client.post(
            "/auth/register",
            json={
                "name": "User One",
                "email": "user1@example.com",
                "password": "samepassword"
            }
        )

        client.post(
            "/auth/register",
            json={
                "name": "User Two",
                "email": "user2@example.com",
                "password": "samepassword"
            }
        )

        # Check that hashes are different (due to salt)
        db = next(override_get_db())
        user1 = db.query(UserModel).filter_by(email="user1@example.com").first()
        user2 = db.query(UserModel).filter_by(email="user2@example.com").first()

        assert user1.hashed_password != user2.hashed_password


class TestRoleBasedAuthorization:
    """Tests for role-based access control."""

    def test_user_has_user_role_by_default(self):
        """Test that new users get USER role by default."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        assert response.json()["role"] == "USER"

    def test_user_role_in_token(self):
        """Test that role is included in token and /me endpoint."""
        register_response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        token = register_response.json()["access_token"]

        # Check /me endpoint
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.json()["role"] == "USER"


class TestTokenGeneration:
    """Tests for JWT token generation and validation."""

    def test_token_contains_user_id(self):
        """Test that JWT token contains user ID."""
        from app.auth.utils import decode_access_token

        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        token = response.json()["access_token"]
        payload = decode_access_token(token)

        assert payload is not None
        assert "sub" in payload  # "sub" contains user_id
        assert payload["sub"].startswith("USER-")

    def test_token_has_expiration(self):
        """Test that JWT token has an expiration time."""
        from app.auth.utils import decode_access_token

        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        token = response.json()["access_token"]
        payload = decode_access_token(token)

        assert payload is not None
        assert "exp" in payload  # "exp" is expiration time


class TestAuthenticationIntegration:
    """Integration tests for complete authentication flows."""

    def test_register_login_access_flow(self):
        """Test complete flow: register, login, access protected endpoint."""
        # 1. Register
        register_response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "john@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Access protected endpoint
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "john@example.com"

    def test_register_gives_immediate_access(self):
        """Test that registration returns a token for immediate login."""
        # Register
        register_response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            }
        )

        token = register_response.json()["access_token"]

        # Should be able to access protected endpoints immediately
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == 200
