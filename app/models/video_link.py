"""
VideoLink model for storing tracked video links.
"""

from sqlalchemy import Column, String, Index
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class VideoLink(BaseModel):
    """
    Model for video tracking links.
    Each link has a unique slug that redirects to a destination URL.
    """
    __tablename__ = "video_links"
    
    # Override created_at from BaseModel as it's specified in requirements
    
    # Columns
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    destination_url = Column(String(1024), nullable=False)
    
    # Relationships - will be populated with back_populates later
    clicks = relationship("Click", back_populates="video_link", cascade="all, delete-orphan")
    calls = relationship("Call", back_populates="video_link", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="video_link", cascade="all, delete-orphan")
    analytics = relationship("VideoAnalytics", back_populates="video_link", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_video_links_slug', slug),
    )
    
    def __repr__(self):
        return f"<VideoLink(id={self.id}, slug='{self.slug}', title='{self.title}')>" 