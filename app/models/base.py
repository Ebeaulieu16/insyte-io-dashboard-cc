"""
Base model with common fields and functionality.
"""

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class BaseModel(Base):
    """Base model with common fields."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 