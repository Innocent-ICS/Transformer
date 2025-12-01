"""
Authentication API routes.
Handles user signup, login, logout, and profile retrieval.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from app.models.user import (
    UserCreate, UserLogin, UserResponse, User,
    create_user, verify_user_credentials, get_user_by_id
)
from app.core.security import create_access_token, decode_access_token


router = APIRouter()
security = HTTPBearer()


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints."""
    token: str
    user: UserResponse


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (email, password, name)
        
    Returns:
        Authentication response with token and user data
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        # Create user
        user = await create_user(user_data)
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        
        # Return response
        return AuthResponse(
            token=access_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detial=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """
    Authenticate a user and return access token.
    
    Args:
        credentials: User login credentials (email, password)
        
    Returns:
        Authentication response with token and user data
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = await verify_user_credentials(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    
    return AuthResponse(
        token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        )
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal).
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    
    Args:
        current_user: Current user from JWT token (dependency injected)
        
    Returns:
        User profile data
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at
    )
