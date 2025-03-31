"""
Security utilities for JWT authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

from app.database import get_db
from app.models.user import User

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-do-not-use-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30
JWT_EXPIRATION_MINUTES = JWT_EXPIRATION_DAYS * 24 * 60

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(data: dict):
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing the claims to encode in the token.
        
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current user from a JWT token.
    
    Args:
        token: JWT access token.
        db: Database session.
        
    Returns:
        User: The current user.
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        # Convert string user_id to integer - this is the key fix!
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid user_id format in token: {user_id}")
            raise credentials_exception
    
    except JWTError:
        logger.error("JWT error", exc_info=True)
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None or not user.is_active:
        logger.warning(f"User {user_id} not found or inactive")
        raise credentials_exception
    
    return user

def get_optional_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current user from a JWT token, but don't raise an exception if authentication fails.
    
    Args:
        token: JWT access token.
        db: Database session.
        
    Returns:
        User or None: The current user or None if authentication fails.
    """
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None 