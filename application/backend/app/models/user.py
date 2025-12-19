"""
User model and database operations.
Handles user data structures and database interactions.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.core.database import get_supabase_client
from app.core.security import hash_password, verify_password
import re


# Pydantic models for request/response
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: str
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class User(BaseModel):
    """Internal user model with all fields."""
    id: str
    email: str
    name: str
    password_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Database operations
async def create_user(user_data: UserCreate) -> User:
    """
    Create a new user in the database.
    
    Args:
        user_data: User registration data
        
    Returns:
        Created user object
        
    Raises:
        ValueError: If email already exists
    """
    supabase = get_supabase_client()
    
    # Check if user already exists
    existing = supabase.table('users').select('id').eq('email', user_data.email).execute()
    if existing.data:
        raise ValueError("Email already registered")
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Insert user
    result = supabase.table('users').insert({
        'email': user_data.email,
        'name': user_data.name,
        'password_hash': password_hash,
        'created_at': datetime.utcnow().isoformat()
    }).execute()
    
    if not result.data:
        raise ValueError("Failed to create user")
    
    return User(**result.data[0])


async def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email address.
    
    Args:
        email: User's email address
        
    Returns:
        User object if found, None otherwise
    """
    supabase = get_supabase_client()
    
    result = supabase.table('users').select('*').eq('email', email).execute()
    
    if result.data:
        return User(**result.data[0])
    return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        user_id: User's unique ID
        
    Returns:
        User object if found, None otherwise
    """
    supabase = get_supabase_client()
    
    result = supabase.table('users').select('*').eq('id', user_id).execute()
    
    if result.data:
        return User(**result.data[0])
    return None


async def verify_user_credentials(email: str, password: str) -> Optional[User]:
    """
    Verify user credentials for login.
    
    Args:
        email: User's email
        password: Plain text password
        
    Returns:
        User object if credentials are valid, None otherwise
    """
    user = await get_user_by_email(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user
