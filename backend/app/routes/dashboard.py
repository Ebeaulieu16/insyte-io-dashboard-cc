"""
Dashboard routes module.
Contains endpoints for global KPIs and metrics overview.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    """
    Get global dashboard metrics and KPIs.
    
    Returns:
        dict: A dictionary containing dashboard metrics.
    """
    # Placeholder for dashboard metrics logic (to be implemented)
    return {
        "message": "Dashboard metrics endpoint",
        "metrics": {
            "total_views": 0,
            "total_revenue": 0,
            "total_calls": 0,
            "conversion_rate": 0,
        }
    }
