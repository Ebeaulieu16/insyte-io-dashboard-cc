"""
VideoAnalytics model for storing YouTube performance metrics.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel

class VideoAnalytics(BaseModel):
    """
    Model for storing YouTube video analytics.
    Records views, likes, comments, engagement rate, and view duration.
    """
    __tablename__ = "video_analytics"
    
    # Columns
    video_id = Column(String(255), nullable=False, index=True)  # YouTube video ID
    slug = Column(String(255), ForeignKey("video_links.slug", ondelete="CASCADE"), nullable=False, index=True)
    views = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)
    comments = Column(Integer, nullable=False, default=0)
    engagement_rate = Column(Float, nullable=False, default=0.0)
    avg_view_duration = Column(Float, nullable=False, default=0.0)  # in seconds
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    video_link = relationship("VideoLink", back_populates="analytics")
    
    # Indexes
    __table_args__ = (
        Index('idx_video_analytics_slug', slug),
        Index('idx_video_analytics_video_id', video_id),
        Index('idx_video_analytics_last_updated', last_updated),
    )
    
    def __repr__(self):
        return f"<VideoAnalytics(id={self.id}, video_id='{self.video_id}', views={self.views}, engagement_rate={self.engagement_rate})>" 