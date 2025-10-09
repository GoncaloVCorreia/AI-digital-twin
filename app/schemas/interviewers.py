"""
User Pydantic schemas.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    
class User(UserBase):
    """User response schema."""
    id: int
    username: str
    created_at: datetime
   
    
    class Config:
        from_attributes = True

class UserInDB(User):
    """User schema with password hash."""
    hashed_password: str

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    username: str
    expires_in: int

class TokenData(BaseModel):
    """Token data for validation."""
    username: Optional[str] = None