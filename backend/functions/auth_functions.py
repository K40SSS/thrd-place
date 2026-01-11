"""
Authentication business logic and utility functions.
Handles user registration, login, token generation, and password validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import bcrypt
from fastapi import HTTPException, status
from supabase import Client
from pydantic import EmailStr

from config import settings
from models import RegisterRequest, AuthResponse


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hashed version.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if passwords match, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token data
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def validate_school_email(email: EmailStr) -> bool:
    """
    Validate that email is from an educational institution.
    Currently checks for common university domain patterns.
    Can be extended with a whitelist of approved schools.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is from a school domain, False otherwise
    """
    # List of common academic email domains
    academic_domains = [
        '.edu', '.ac.uk', '.edu.au', '.ac.ca', '.edu.br', '.de',
        '.fr', '.jp', '.cn', '.in', '.ac.nz', '@mcmaster.ca', '@waterloo.ca'
    ]
    
    email_lower = str(email).lower()
    return any(email_lower.endswith(domain) for domain in academic_domains)


async def register_user(
    db: Client,
    register_data: RegisterRequest
) -> AuthResponse:
    """
    Register a new user in the system.
    
    Args:
        db: Supabase client
        register_data: Registration data
        
    Returns:
        AuthResponse with user data and access token
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Validate school email
    if not validate_school_email(register_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please use a valid school email address (e.g., .edu, .ac.uk)"
        )
    
    # Check if user already exists
    try:
        existing_user = db.table('users').select('id').eq('email', register_data.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    except Exception as e:
        if "400" not in str(e):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during registration"
            )
    
    # Hash password
    hashed_password = hash_password(register_data.password)
    print(f"[REGISTER] Password hashed for {register_data.email}")
    
    # Create user in database
    try:
        user_data = {
            'email': register_data.email,
            'password_hash': hashed_password,
            'first_name': register_data.first_name,
            'last_name': register_data.last_name,
            'school': register_data.school,
            'bio': '',
            'rating': None
        }
        
        print(f"[REGISTER] Inserting user with fields: {list(user_data.keys())}")
        response = db.table('users').insert(user_data).execute()
        user = response.data[0]
        print(f"[REGISTER] User created successfully: {user['id']} | Email: {user['email']}")
        
        # Create access token
        access_token = create_access_token(data={"sub": user['id'], "email": user['email']})
        
        return AuthResponse(
            id=user['id'],
            email=user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            school=user['school'],
            access_token=access_token,
            token_type="bearer"
        )
    
    except Exception as e:
        print(f"[REGISTER] Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


async def login_user(
    db: Client,
    email: EmailStr,
    password: str
) -> AuthResponse:
    """
    Authenticate a user and return access token.
    
    Args:
        db: Supabase client
        email: User email
        password: User password
        
    Returns:
        AuthResponse with user data and access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Fetch user from database
        response = db.table('users').select('*').eq('email', email).execute()
        print(f"[LOGIN] Database query for email '{email}': {response.data if response.data else 'NO USER FOUND'}")
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = response.data[0]
        print(f"[LOGIN] User found: {user.get('email')} | Has password_hash: {'password_hash' in user}")
        
        # Verify password
        if 'password_hash' not in user:
            print(f"[LOGIN] ERROR: No password_hash field! Available fields: {list(user.keys())}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        password_match = verify_password(password, user['password_hash'])
        print(f"[LOGIN] Password verification result: {password_match}")
        
        if not password_match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user['id'], "email": user['email']})
        
        return AuthResponse(
            id=user['id'],
            email=user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            school=user['school'],
            access_token=access_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN] Exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
