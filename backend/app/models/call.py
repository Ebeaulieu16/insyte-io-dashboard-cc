"""
Call model for tracking calendar appointments.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.base import BaseModel

class CallStatus(str, enum.Enum):
    """Enumeration of possible call statuses."""
    BOOKED = "booked"
    LIVE = "live"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class Call(BaseModel):
    """
    Model for tracking calendar appointments.
    Records email, status, and timestamp information.
    """
    __tablename__ = "calls"
    
    # Columns
    slug = Column(String(255), ForeignKey("video_links.slug", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    status = Column(
        Enum(CallStatus, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, 
        default=CallStatus.BOOKED, 
        index=True
    )
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    video_link = relationship("VideoLink", back_populates="calls")
    
    # Indexes
    __table_args__ = (
        Index('idx_calls_slug', slug),
        Index('idx_calls_email', email),
        Index('idx_calls_status', status),
        Index('idx_calls_timestamp', timestamp),
        Index('idx_calls_slug_status', slug, status),
    )
    
    def __repr__(self):
        return f"<Call(id={self.id}, slug='{self.slug}', status='{self.status}', email='{self.email}')>" 