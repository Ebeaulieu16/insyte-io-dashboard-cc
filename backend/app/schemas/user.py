"""
User schema module.
Pydantic schemas for user authentication.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base schema for user operations."""
    email: EmailStr = Field(..., description="User's email address")
    
class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., description="User's password")
    
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        orm_mode = True
        
class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    user: UserResponse = Field(..., description="User data") 