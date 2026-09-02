"""
FinSight — Authentication Dependencies

FastAPI dependencies for authentication and authorization.

Key Architecture Concepts:
    - Dependency Injection: FastAPI's Depends() system
    - Security: OAuth2 password bearer authentication
    - Authorization: Role-based access control
    - Separation of Concerns: Auth logic separate from routes

FastAPI Dependencies:
    Dependencies are functions that run before route handlers.
    They can:
        - Validate requests (e.g., check for valid tokens)
        - Extract data (e.g., get current user from token)
        - Raise errors (e.g., 401 Unauthorized)
        - Inject values into route handlers (e.g., current_user)
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.config import get_db_session
from app.auth.utils import get_user_id_from_token
from app.services.auth_service import AuthService
from app.repositories.postgresql_user_repository import PostgreSQLUserRepository
from app.domain.user import User, UserRole


# OAuth2PasswordBearer is a FastAPI class that:
#   1. Tells FastAPI this endpoint requires authentication
#   2. Extracts the token from the Authorization header
#   3. Provides it to dependency functions
#
# The tokenUrl parameter tells the API docs where to get tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    """
    Dependency that provides an AuthService instance.

    This demonstrates dependency injection in FastAPI:
        1. get_db_session provides a database session
        2. We create a repository with that session
        3. We create a service with that repository
        4. FastAPI injects the service into route handlers

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        AuthService instance
    """
    user_repository = PostgreSQLUserRepository(db)
    return AuthService(user_repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency that extracts and validates the current user from a JWT token.

    This is the core authentication dependency. Use it in route handlers
    to require authentication and get the current user.

    Flow:
        1. oauth2_scheme extracts the token from Authorization header
        2. Decode the token to get the user ID
        3. Look up the user in the database
        4. Return the user or raise 401 Unauthorized

    Usage in a route:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.name}"}

    Args:
        token: JWT token from Authorization header (injected by oauth2_scheme)
        auth_service: AuthService instance (injected by get_auth_service)

    Returns:
        The authenticated User object

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    # Extract user ID from token
    user_id = get_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = auth_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that requires the current user to have ADMIN role.

    This demonstrates role-based authorization (RBAC).
    It builds on get_current_user by adding an additional check.

    Usage in a route:
        @app.get("/admin")
        def admin_only(current_user: User = Depends(require_admin)):
            return {"message": "Admin access granted"}

    Args:
        current_user: Authenticated user (injected by get_current_user)

    Returns:
        The authenticated admin User object

    Raises:
        HTTPException 403: If user is not an admin
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Dependency that extracts the current user if a token is provided.

    Unlike get_current_user, this doesn't raise an error if no token
    is present. Use this for routes that are public but behave differently
    for authenticated users.

    Args:
        token: Optional JWT token from Authorization header
        auth_service: AuthService instance

    Returns:
        User if authenticated, None otherwise
    """
    if token is None:
        return None

    user_id = get_user_id_from_token(token)
    if user_id is None:
        return None

    return auth_service.get_user_by_id(user_id)
