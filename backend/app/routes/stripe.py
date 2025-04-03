"""
Stripe routes module.
Contains endpoints for Stripe data and metrics.
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.models.integration import Integration
from app.models.user import User
from app.utils.stripe_api import get_stripe_data_for_integration

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/api/stripe/data")
async def get_stripe_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get Stripe data for the current user.
    
    Returns:
        dict: Stripe data including payments and metrics
    """
    try:
        # Get user ID from authenticated user or return error
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        user_id = current_user.id
        
        # Check if user has Stripe integration
        integration_query = select(Integration).where(
            Integration.platform == "stripe",
            Integration.user_id == user_id
        )
        
        integration = await db.execute(integration_query)
        integration = integration.scalars().first()
        
        is_integration_connected = False
        api_key = None
        
        if integration:
            # Check if integration is connected
            if hasattr(integration, 'status') and integration.status == 'connected':
                is_integration_connected = True
            elif hasattr(integration, 'is_connected') and integration.is_connected:
                is_integration_connected = True
                
            # Get API key from extra_data if available
            if hasattr(integration, 'extra_data') and integration.extra_data:
                try:
                    if isinstance(integration.extra_data, str):
                        extra_data = json.loads(integration.extra_data)
                    else:
                        extra_data = integration.extra_data
                        
                    api_key = extra_data.get('api_key')
                    if api_key:
                        logger.info(f"Found Stripe API key for user {user_id}")
                except Exception as e:
                    logger.error(f"Error parsing extra_data: {str(e)}")
        
        # If no API key found in database, return demo data
        if not api_key:
            logger.info("No Stripe API key found in database, using demo data")
        
        # If integration is connected and we have an API key, fetch real data
        if is_integration_connected and api_key:
            logger.info("Fetching real Stripe data from API")
            
            # Fetch real data from Stripe API
            stripe_data = await get_stripe_data_for_integration(api_key)
            
            return {
                "message": "Real Stripe data from API",
                "data": stripe_data
            }
        else:
            # Return demo data
            logger.info("Returning demo Stripe data")
            return {
                "message": "Demo Stripe data (no integration connected)",
                "data": get_demo_stripe_data()
            }
    
    except Exception as e:
        logger.error(f"Error in get_stripe_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Stripe data: {str(e)}"
        )

def get_demo_stripe_data() -> Dict[str, Any]:
    """
    Get demo Stripe data for testing.
    
    Returns:
        dict: Demo Stripe data
    """
    return {
        "message": "Demo Stripe data",
        "payments": [
            {
                "id": "pi_1234567890",
                "amount": 49.99,
                "currency": "USD",
                "status": "succeeded",
                "created": "2025-03-28T10:30:00",
                "customer_email": "customer1@example.com",
                "customer_name": "John Doe",
                "payment_method": "card",
                "description": "Monthly subscription"
            },
            {
                "id": "pi_0987654321",
                "amount": 99.99,
                "currency": "USD",
                "status": "succeeded",
                "created": "2025-03-27T14:45:00",
                "customer_email": "customer2@example.com",
                "customer_name": "Jane Smith",
                "payment_method": "card",
                "description": "Annual subscription"
            }
        ],
        "account": {
            "id": "acct_demo123",
            "email": "business@example.com",
            "business_name": "Demo Business",
            "country": "US",
            "default_currency": "USD",
            "details_submitted": True,
            "payouts_enabled": True,
            "charges_enabled": True
        },
        "metrics": {
            "totalRevenue": 1249.75,
            "totalPayments": 25,
            "successfulPayments": 23,
            "averagePayment": 54.34,
            "monthlyData": [
                {"month": "Nov 2024", "count": 3, "revenue": 149.97},
                {"month": "Dec 2024", "count": 4, "revenue": 199.96},
                {"month": "Jan 2025", "count": 5, "revenue": 249.95},
                {"month": "Feb 2025", "count": 4, "revenue": 199.96},
                {"month": "Mar 2025", "count": 6, "revenue": 299.94},
                {"month": "Apr 2025", "count": 3, "revenue": 149.97}
            ]
        }
    }
