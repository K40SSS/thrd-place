"""
Authentication routes for user registration, login, and token management.
Provides endpoints for account creation and credential verification.
"""

from fastapi import APIRouter, HTTPException, status, Depends

from models import RegisterRequest, LoginRequest, AuthResponse
from supabase_client import get_supabase_client
from functions.auth_functions import register_user, login_user

# Create router for authentication endpoints
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal Server Error"}
    }
)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db = Depends(get_supabase_client)
) -> AuthResponse:
    """
    Register a new user account.
    
    - **email**: School email address (must be from .edu or similar academic domain)
    - **password**: Minimum 8 characters
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **school**: Name of the school/university
    
    Returns an access token that should be used for subsequent authenticated requests.
    """
    return await register_user(db, register_data)


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    db = Depends(get_supabase_client)
) -> AuthResponse:
    """
    Login with email and password.
    
    - **email**: School email address
    - **password**: Password
    
    Returns an access token for authenticated requests.
    """
    return await login_user(db, login_data.email, login_data.password)


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the auth service is running.
    """
    return {"status": "healthy", "message": "Authentication service is running"}
