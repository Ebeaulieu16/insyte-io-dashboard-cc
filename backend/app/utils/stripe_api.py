"""
Stripe API utility functions.
Handles fetching real data from the Stripe API using API keys.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

async def fetch_stripe_account_data(api_key: str) -> Dict[str, Any]:
    """
    Fetch account data from the Stripe API.
    
    Args:
        api_key: Stripe API key
        
    Returns:
        dict: Account data
    """
    try:
        logger.info("Fetching Stripe account data")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.stripe.com/v1/account", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched Stripe account data for: {data.get('email', 'Unknown')}")
            
            return {
                "id": data.get("id"),
                "email": data.get("email"),
                "business_name": data.get("business_profile", {}).get("name"),
                "country": data.get("country"),
                "default_currency": data.get("default_currency"),
                "details_submitted": data.get("details_submitted", False),
                "payouts_enabled": data.get("payouts_enabled", False),
                "charges_enabled": data.get("charges_enabled", False)
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Stripe account data: {e.response.status_code} - {e.response.text}")
        return {"error": f"Stripe API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching Stripe account data: {str(e)}")
        return {"error": f"Error: {str(e)}"}

async def fetch_stripe_payments(api_key: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch payments from Stripe.
    
    Args:
        api_key: Stripe API key
        limit: Maximum number of payments to fetch
        
    Returns:
        list: List of payment data
    """
    try:
        logger.info(f"Fetching up to {limit} Stripe payments")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        params = {
            "limit": limit,
            "expand[]": "data.customer"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.stripe.com/v1/payment_intents", headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" not in data or len(data["data"]) == 0:
                logger.warning("No payments found in Stripe account")
                return []
            
            payments = []
            for item in data["data"]:
                payment = {
                    "id": item.get("id"),
                    "amount": item.get("amount") / 100,  # Convert from cents to dollars
                    "currency": item.get("currency", "usd").upper(),
                    "status": item.get("status"),
                    "created": datetime.fromtimestamp(item.get("created", 0)).isoformat(),
                    "customer_email": item.get("customer", {}).get("email", "Unknown"),
                    "customer_name": item.get("customer", {}).get("name", "Unknown"),
                    "payment_method": item.get("payment_method_types", ["unknown"])[0],
                    "description": item.get("description", "")
                }
                payments.append(payment)
            
            logger.info(f"Successfully fetched {len(payments)} payments from Stripe")
            return payments
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Stripe payments: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching Stripe payments: {str(e)}")
        return []

async def get_stripe_data_for_integration(api_key: str) -> Dict[str, Any]:
    """
    Get comprehensive Stripe data.
    
    Args:
        api_key: Stripe API key
        
    Returns:
        dict: Complete Stripe data including account info and payments
    """
    try:
        # Fetch account data
        account_data = await fetch_stripe_account_data(api_key)
        if "error" in account_data:
            return {
                "message": account_data["error"],
                "payments": [],
                "account": {},
                "metrics": {}
            }
        
        # Fetch payments
        payments = await fetch_stripe_payments(api_key)
        
        # Calculate metrics
        total_revenue = sum(payment["amount"] for payment in payments)
        successful_payments = [p for p in payments if p["status"] == "succeeded"]
        total_successful = len(successful_payments)
        
        # Get payment counts by month (last 6 months)
        now = datetime.now()
        monthly_data = []
        
        for i in range(5, -1, -1):
            month_start = datetime(now.year, now.month, 1) - timedelta(days=30*i)
            month_name = month_start.strftime("%b %Y")
            
            # Filter payments for this month
            month_payments = [
                p for p in payments 
                if p["status"] == "succeeded" and 
                datetime.fromisoformat(p["created"]).year == month_start.year and
                datetime.fromisoformat(p["created"]).month == month_start.month
            ]
            
            monthly_revenue = sum(p["amount"] for p in month_payments)
            
            monthly_data.append({
                "month": month_name,
                "count": len(month_payments),
                "revenue": monthly_revenue
            })
        
        return {
            "message": "Real Stripe data from API",
            "payments": payments,
            "account": account_data,
            "metrics": {
                "totalRevenue": total_revenue,
                "totalPayments": len(payments),
                "successfulPayments": total_successful,
                "averagePayment": total_revenue / total_successful if total_successful > 0 else 0,
                "monthlyData": monthly_data
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting Stripe data: {str(e)}")
        return {
            "message": f"Error: {str(e)}",
            "payments": [],
            "account": {},
            "metrics": {}
        }
