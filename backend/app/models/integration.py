"""
Integration model for storing OAuth tokens.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
import enum

from app.models.base import BaseModel

class IntegrationType(str, enum.Enum):
    """Enumeration of integration types."""
    YOUTUBE = "youtube"
    STRIPE = "stripe"
    CALENDLY = "calendly"
    CALCOM = "calcom"

class Integration(BaseModel):
    """
    Model for storing integration tokens and connection status.
    Records platform, access_token, refresh_token, and expiration.
    """
    __tablename__ = "integrations"
    
    # Columns
    platform = Column(
        String(50), 
        nullable=False, 
        index=True,
        unique=True
    )
    is_connected = Column(Boolean, nullable=False, default=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Additional columns for platform-specific data
    api_key = Column(String(255), nullable=True)  # For platforms that use API keys
    account_name = Column(String(255), nullable=True)
    account_id = Column(String(255), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_integrations_platform', platform),
    )
    
    def __repr__(self):
        return f"<Integration(id={self.id}, platform='{self.platform}', connected={self.is_connected})>" 