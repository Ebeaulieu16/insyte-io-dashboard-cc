"""
User authentication routes.
Endpoints for user registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.security import create_access_token, get_current_user

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["user-authentication"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User registration data.
        db: Database session.
        
    Returns:
        TokenResponse: JWT access token and user data.
        
    Raises:
        HTTPException: If the email is already registered.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.warning(f"Attempted registration with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create new user
        user = User(email=user_data.email)
        user.set_password(user_data.password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    except IntegrityError:
        db.rollback()
        logger.error("IntegrityError during user registration", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again.",
        )

@router.post("/token", response_model=TokenResponse)
def login(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    
    Args:
        user_credentials: User login credentials.
        response: FastAPI response object.
        db: Database session.
        
    Returns:
        TokenResponse: JWT access token and user data.
        
    Raises:
        HTTPException: If the credentials are invalid.
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    # Verify user and password
    if not user or not user.verify_password(user_credentials.password):
        logger.warning(f"Invalid login attempt for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's information.
    
    Args:
        current_user: Current authenticated user.
        
    Returns:
        UserResponse: Current user's data.
    """
    return current_user

@router.post("/logout")
def logout(response: Response):
    """
    Logout the current user.
    Client-side should remove the token.
    
    Args:
        response: FastAPI response object.
        
    Returns:
        dict: Success message.
    """
    return {"message": "Successfully logged out"} 