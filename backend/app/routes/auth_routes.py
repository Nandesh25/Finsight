"""
FinSight — Authentication Routes

FastAPI routes for user registration and login.

Key Architecture Concepts:
    - Route Layer: HTTP request/response handling
    - Dependency Injection: Services injected via Depends()
    - Error Handling: Proper HTTP status codes for auth errors
    - Security: Password hashing, JWT tokens, proper error messages

Architecture Flow:
    HTTP Request -> Route -> Service -> Repository -> Database
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    AuthErrorResponse
)
from app.services.auth_service import AuthService
from app.auth.dependencies import get_auth_service, get_current_user
from app.domain.user import User


# Create a router for authentication endpoints
# This groups related routes together and can be included in the main app
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"model": AuthErrorResponse}},
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Returns a JWT access token."
)
async def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Register a new user.

    This endpoint:
        1. Validates the request data (Pydantic does this automatically)
        2. Hashes the password
        3. Creates the user in the database
        4. Generates a JWT token
        5. Returns the token so the user is immediately logged in

    Args:
        request: Registration data (name, email, password)
        auth_service: AuthService instance (dependency injection)

    Returns:
        TokenResponse with access token and user info

    Raises:
        HTTPException 400: If email already exists or validation fails
    """
    try:
        # Register the user (password is hashed in the service)
        user = auth_service.register_user(
            name=request.name,
            email=request.email,
            password=request.password
        )

        # Create an access token for immediate login
        access_token = auth_service.create_access_token_for_user(user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value
        )

    except ValueError as e:
        # User already exists or validation failed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticate a user and receive a JWT access token."
)
async def login(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Login and receive an access token.

    This endpoint:
        1. Validates the email and password
        2. Authenticates the user (verifies password hash)
        3. Generates a JWT token
        4. Returns the token

    Security note: We return a generic "Invalid credentials" message
    whether the email doesn't exist or the password is wrong.
    This prevents attackers from enumerating valid email addresses.

    Args:
        request: Login credentials (email, password)
        auth_service: AuthService instance (dependency injection)

    Returns:
        TokenResponse with access token and user info

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Authenticate the user
    user = auth_service.authenticate_user(
        email=request.email,
        password=request.password
    )

    if user is None:
        # Authentication failed - don't reveal whether email or password was wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = auth_service.create_access_token_for_user(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        role=user.role.value
    )


@router.get(
    "/me",
    response_model=dict,
    summary="Get current user",
    description="Get the currently authenticated user's information."
)
async def get_me(current_user: User = Depends(get_current_user)) -> dict:
    """
    Get the current user's information.

    This is a protected endpoint that requires authentication.
    It demonstrates how to use the get_current_user dependency.

    Args:
        current_user: The authenticated user (dependency injection)

    Returns:
        User information

    Raises:
        HTTPException 401: If not authenticated
    """
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
        "total_balance": current_user.get_total_balance()
    }
