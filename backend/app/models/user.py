"""
User model for authentication.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from passlib.hash import bcrypt
import uuid

from app.models.base import BaseModel

class User(BaseModel):
    """User model for authentication."""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Generate a unique API key for each user
    api_key = Column(String(64), unique=True, index=True, nullable=False, 
                     default=lambda: uuid.uuid4().hex)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    
    def set_password(self, password):
        """Hash the password using bcrypt."""
        self.password_hash = bcrypt.hash(password)
    
    def verify_password(self, password):
        """Verify the password against the stored hash."""
        return bcrypt.verify(password, self.password_hash) 