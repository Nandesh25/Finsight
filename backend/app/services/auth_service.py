"""
FinSight — Authentication Service

This module implements authentication and authorization business logic.

Key Architecture Concepts:
    - Service Layer: Business logic separate from routes and repositories
    - Authentication: Verifying user identity (login)
    - Authorization: Verifying user permissions (roles)
    - Dependency Injection: Repository injected via constructor
    - Separation of Concerns: Auth logic isolated from domain logic

OOP Concepts:
    - Encapsulation: Auth details hidden behind service methods
    - Single Responsibility: This service only handles auth concerns
    - Abstraction: Complex auth operations exposed as simple methods
"""

from typing import Optional
from datetime import timedelta

from app.domain.user import User, UserRole
from app.repositories.postgresql_user_repository import PostgreSQLUserRepository
from app.auth.utils import hash_password, verify_password, create_access_token


class AuthService:
    """
    Service for handling authentication and authorization.

    This service encapsulates all authentication-related business logic:
        - User registration with password hashing
        - User login with credential verification
        - JWT token generation
        - User lookup for protected routes

    Architecture:
        Route -> AuthService -> Repository -> Database
    """

    def __init__(self, user_repository: PostgreSQLUserRepository):
        """
        Initialize the authentication service.

        Dependency Injection: The repository is passed in rather than
        created here. This makes testing easier and follows SOLID principles.

        Args:
            user_repository: Repository for user data access
        """
        self._user_repository = user_repository
        self._next_user_id = 1  # Simple counter for generating user IDs

    def register_user(self, name: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """
        Register a new user with password hashing.

        This method demonstrates secure user registration:
            1. Check if email already exists
            2. Hash the password (never store plain text)
            3. Generate a unique user ID
            4. Create and persist the user

        Args:
            name: User's full name
            email: User's email address (must be unique)
            password: Plain-text password (will be hashed)
            role: User role (defaults to USER)

        Returns:
            The newly created User object

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Check if user with this email already exists
        existing_user = self._user_repository.find_by_email(email)
        if existing_user:
            raise ValueError(f"User with email '{email}' already exists.")

        # Hash the password - NEVER store plain-text passwords
        hashed_password = hash_password(password)

        # Generate a unique user ID
        user_id = self._generate_user_id()

        # Create the user domain object
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            role=role
        )

        # Persist to database through repository
        created_user = self._user_repository.create(user)

        return created_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        This method demonstrates secure authentication:
            1. Find user by email
            2. Verify password using bcrypt
            3. Return user if valid, None otherwise

        NEVER return specific error messages like "email not found" or
        "wrong password" - this leaks information to attackers.

        Args:
            email: User's email address
            password: Plain-text password to verify

        Returns:
            User object if authentication succeeds, None otherwise
        """
        # Find user by email
        user = self._user_repository.find_by_email(email)

        if user is None:
            # User doesn't exist - return None
            # Don't reveal whether the email exists
            return None

        if user.hashed_password is None:
            # User has no password (shouldn't happen, but be safe)
            return None

        # Verify the password
        if not verify_password(password, user.hashed_password):
            # Wrong password - return None
            return None

        # Authentication successful
        return user

    def create_access_token_for_user(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token for a user.

        JWT tokens are stateless - the server doesn't store them.
        The token contains the user ID, which is used to identify
        the user on subsequent requests.

        Args:
            user: The user to create a token for
            expires_delta: Optional custom expiration time

        Returns:
            JWT access token string
        """
        # Create token data (called "claims" in JWT terminology)
        # "sub" (subject) is the standard claim for user identity
        token_data = {
            "sub": user.user_id,
            "role": user.role.value
        }

        # Generate and return the token
        return create_access_token(token_data, expires_delta)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        This is used by the authentication dependency to get the
        current user from a JWT token.

        Args:
            user_id: The user ID to look up

        Returns:
            User object if found, None otherwise
        """
        return self._user_repository.find_by_id(user_id)

    def _generate_user_id(self) -> str:
        """
        Generate a unique user ID.

        In a real system, this might use UUID or database auto-increment.
        For simplicity, we use a counter with proper formatting.

        Returns:
            Unique user ID string (e.g., "USER-000001")
        """
        # Find the highest existing user ID number
        all_users = self._user_repository.list_all()
        if all_users:
            # Extract numbers from user IDs like "USER-000001"
            max_id = max(
                int(user.user_id.split("-")[1]) for user in all_users
                if "-" in user.user_id and user.user_id.split("-")[1].isdigit()
            )
            self._next_user_id = max_id + 1
        else:
            self._next_user_id = 1

        user_id = f"USER-{self._next_user_id:06d}"
        self._next_user_id += 1
        return user_id
