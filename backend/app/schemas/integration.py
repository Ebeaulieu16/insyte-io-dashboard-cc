"""
Pydantic schemas for integration data validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class IntegrationBase(BaseModel):
    """Base schema for integration data."""
    platform: str = Field(..., description="Integration platform name")

class IntegrationCreate(IntegrationBase):
    """Schema for creating a new integration record."""
    access_token: Optional[str] = Field(None, description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration timestamp")
    api_key: Optional[str] = Field(None, description="API key (for non-OAuth platforms)")
    account_name: Optional[str] = Field(None, description="Account name")
    account_id: Optional[str] = Field(None, description="Account ID")

class IntegrationUpdate(BaseModel):
    """Schema for updating integration records."""
    status: Optional[str] = Field(None, description="Connection status")
    access_token: Optional[str] = Field(None, description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration timestamp")
    last_sync: Optional[datetime] = Field(None, description="Last successful data sync timestamp")
    api_key: Optional[str] = Field(None, description="API key (for non-OAuth platforms)")
    account_name: Optional[str] = Field(None, description="Account name")
    account_id: Optional[str] = Field(None, description="Account ID")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional platform-specific data")

class IntegrationResponse(IntegrationBase):
    """Schema for integration responses (public fields only)."""
    id: int
    status: str = Field(..., description="Status: connected, disconnected, error")
    last_sync: Optional[datetime] = None
    account_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    extra_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class IntegrationStatus(BaseModel):
    """Schema for integration status responses."""
    platform: str
    status: str = Field(..., description="Status: connected, disconnected, error")
    account_name: Optional[str] = None
    last_sync: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        
class IntegrationStatusList(BaseModel):
    """Schema for list of integration statuses."""
    integrations: List[IntegrationStatus] 