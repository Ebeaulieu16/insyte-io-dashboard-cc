"""
Click model for tracking link clicks.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel

class Click(BaseModel):
    """
    Model for tracking clicks on video links.
    Records timestamp, IP address, and referrer information.
    """
    __tablename__ = "clicks"
    
    # Columns
    slug = Column(String(255), ForeignKey("video_links.slug", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 can be up to 45 chars
    referrer = Column(String(1024), nullable=True)
    
    # Relationships
    video_link = relationship("VideoLink", back_populates="clicks")
    
    # Indexes
    __table_args__ = (
        Index('idx_clicks_slug', slug),
        Index('idx_clicks_timestamp', timestamp),
        Index('idx_clicks_slug_timestamp', slug, timestamp),
    )
    
    def __repr__(self):
        return f"<Click(id={self.id}, slug='{self.slug}', timestamp='{self.timestamp}')>" 