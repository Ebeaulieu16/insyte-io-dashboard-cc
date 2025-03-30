"""
Integration model for storing OAuth tokens.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Index, Integer, JSON
from sqlalchemy.sql import func
import enum
import json

from app.models.base import BaseModel

class IntegrationType(str, enum.Enum):
    """Enumeration of integration types."""
    YOUTUBE = "youtube"
    STRIPE = "stripe"
    CALENDLY = "calendly"
    CALCOM = "calcom"

class IntegrationStatus(str, enum.Enum):
    """Enumeration of integration status."""
    PENDING = "pending"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    ACTIVE = "active"

class IntegrationAuthType(str, enum.Enum):
    """Enumeration of authentication types."""
    OAUTH = "oauth"
    API_KEY = "api_key"

class Integration(BaseModel):
    """
    Model for storing integration details.
    Includes OAuth tokens, account information, and platform-specific data.
    """
    __tablename__ = "integrations"
    
    # User who owns this integration
    user_id = Column(Integer, nullable=False, index=True)
    
    # Integration type and status
    platform = Column(String(50), nullable=False)
    status = Column(String(50), default=IntegrationStatus.PENDING, nullable=False)
    
    # Authentication type (OAuth or API Key)
    auth_type = Column(String(20), default=IntegrationAuthType.OAUTH, nullable=False)
    
    # Account details
    account_id = Column(String(255), nullable=True, index=True)
    account_name = Column(String(255), nullable=True)
    
    # OAuth tokens
    access_token = Column(String(512), nullable=True)
    refresh_token = Column(String(512), nullable=True)
    token_type = Column(String(50), default="bearer", nullable=True)
    scope = Column(String(255), nullable=True)
    
    # Token expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Last synced timestamp
    last_sync = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Additional metadata as JSON - renamed to avoid SQLAlchemy reserved name conflict
    extra_data = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_integration_user_platform', user_id, platform),
        Index('idx_integration_account', account_id),
    )
    
    def __repr__(self):
        return f"<Integration(id={self.id}, user_id={self.user_id}, platform='{self.platform}', account='{self.account_id}')>"
    
    # Property to get the API key if stored in extra_data
    @property
    def api_key(self):
        """Get the API key from extra_data if auth_type is API_KEY."""
        if self.auth_type == IntegrationAuthType.API_KEY and self.extra_data:
            try:
                if isinstance(self.extra_data, str):
                    data = json.loads(self.extra_data)
                else:
                    data = self.extra_data
                return data.get("api_key")
            except (ValueError, AttributeError):
                return None
        return None
    
    # Property to check if the integration is connected
    @property
    def is_connected(self):
        """Check if the integration is connected."""
        return self.status in [IntegrationStatus.CONNECTED, IntegrationStatus.ACTIVE] 