"""
Payment model for tracking payments.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel

class Payment(BaseModel):
    """
    Model for tracking payments.
    Records email, amount, currency, and timestamp information.
    """
    __tablename__ = "payments"
    
    # Columns
    slug = Column(String(255), ForeignKey("video_links.slug", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")  # ISO 4217 currency code
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    video_link = relationship("VideoLink", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index('idx_payments_slug', slug),
        Index('idx_payments_email', email),
        Index('idx_payments_timestamp', timestamp),
        Index('idx_payments_slug_email', slug, email),
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, slug='{self.slug}', amount={self.amount}, currency='{self.currency}')>" 