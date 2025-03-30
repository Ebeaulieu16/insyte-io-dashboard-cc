"""
Authentication helper functions.
Utilities for handling user authentication and authorization in API endpoints.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, Query
import logging

from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user

# Set up logger
logger = logging.getLogger(__name__)

def filter_by_user_id(query: Query, user_id: int, user_id_column) -> Query:
    """
    Filter a SQLAlchemy query by user ID.
    
    Args:
        query: SQLAlchemy query to filter.
        user_id: User ID to filter by.
        user_id_column: SQLAlchemy column for user ID in the table.
        
    Returns:
        Query: Filtered query.
    """
    return query.filter(user_id_column == user_id)

def get_current_user_data(
    query: Query, 
    user_id_column,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Get data for the current user.
    
    Args:
        query: SQLAlchemy query to filter.
        user_id_column: SQLAlchemy column for user ID in the table.
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        list: Filtered results for the current user.
    """
    # Filter query by user ID
    filtered_query = filter_by_user_id(query, current_user.id, user_id_column)
    
    # Execute query
    return filtered_query.all()

def validate_user_ownership(
    resource_id: int, 
    model, 
    user_id_column,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate that a resource belongs to the current user.
    
    Args:
        resource_id: ID of the resource to check.
        model: SQLAlchemy model for the resource.
        user_id_column: SQLAlchemy column for user ID in the table.
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        model: The requested resource.
        
    Raises:
        HTTPException: If the resource doesn't exist or doesn't belong to the user.
    """
    # Get resource
    resource = db.query(model).filter(model.id == resource_id).first()
    
    # Check if resource exists
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Check if resource belongs to user
    resource_user_id = getattr(resource, user_id_column.name)
    if resource_user_id != current_user.id:
        logger.warning(f"Unauthorized access attempt to resource {resource_id} by user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    
    return resource 