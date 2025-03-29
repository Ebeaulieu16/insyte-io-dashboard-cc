"""
Payment routes module.
Contains endpoints for payment webhooks and transaction processing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
import os
import stripe
import json
import logging
from datetime import datetime

from app.database import get_db
from app.models.payment import Payment
from app.models.integration import Integration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Stripe client with the API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

router = APIRouter(
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

@router.post("/webhook/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint for receiving Stripe webhook events.
    This endpoint handles payment_intent.succeeded events to track payments.
    Also processes events from connected accounts.
    
    Args:
        request: The incoming webhook request
        db: Database session
        
    Returns:
        dict: A simple confirmation message
    """
    # Get the request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Log request receipt
    logger.info(f"Received Stripe webhook: {sig_header}")
    
    if not webhook_secret:
        logger.error("Webhook secret is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret is not configured"
        )
    
    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Check if this event is from a connected account
    account_id = event.get("account")
    dashboard_user_id = None
    
    # If this is from a connected account, find which dashboard user it belongs to
    if account_id:
        logger.info(f"Event from connected account: {account_id}")
        integration = db.query(Integration).filter(
            Integration.platform == "stripe",
            Integration.account_id == account_id
        ).first()
        
        if integration:
            dashboard_user_id = integration.user_id
            logger.info(f"Found integration for dashboard user: {dashboard_user_id}")
        else:
            logger.warning(f"No integration found for account: {account_id}")
    
    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        
        # Extract metadata
        metadata = payment_intent.get("metadata", {})
        slug = metadata.get("slug")
        email = metadata.get("email")
        
        # Log the payment intent
        logger.info(f"Processing payment_intent.succeeded: {payment_intent['id']}")
        logger.info(f"Metadata: {metadata}")
        logger.info(f"Account ID: {account_id}")
        logger.info(f"Dashboard User ID: {dashboard_user_id}")
        
        # For connected accounts, we can use a default slug if none is provided
        if not slug and account_id:
            slug = f"account_{account_id}"
            logger.info(f"Using default slug for connected account: {slug}")
        elif not slug:
            logger.warning(f"No slug in metadata for payment_intent {payment_intent['id']}")
            return {"status": "missing_metadata", "message": "Payment received but no slug provided in metadata"}
        
        if not email:
            # Try to get email from customer if available
            if payment_intent.get("customer"):
                try:
                    customer = stripe.Customer.retrieve(payment_intent["customer"])
                    email = customer.get("email", "unknown@example.com")
                except Exception as e:
                    logger.error(f"Error retrieving customer: {e}")
                    email = "unknown@example.com"
            else:
                email = "unknown@example.com"
                
        try:
            # Create a new payment record with account tracking
            payment = Payment(
                slug=slug,
                email=email,
                amount=payment_intent["amount"] / 100,  # Convert from cents to dollars
                currency=payment_intent["currency"].upper(),
                timestamp=datetime.fromtimestamp(payment_intent["created"]),
                dashboard_user_id=dashboard_user_id,
                stripe_account_id=account_id
            )
            
            # Save to database
            db.add(payment)
            db.commit()
            
            logger.info(f"Payment recorded: {payment}")
            return {"status": "success", "message": "Payment processed successfully"}
            
        except Exception as e:
            logger.error(f"Error recording payment: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error recording payment: {str(e)}"
            )
    
    # Handle account.updated events to update integration status
    elif event["type"] == "account.updated" and account_id:
        account = event["data"]["object"]
        
        try:
            # Update integration status based on account details
            integration = db.query(Integration).filter(
                Integration.platform == "stripe",
                Integration.account_id == account_id
            ).first()
            
            if integration:
                # Update account name if available
                if account.get("business_profile", {}).get("name"):
                    integration.account_name = account["business_profile"]["name"]
                
                # Update metadata with additional account information
                if not integration.metadata:
                    integration.metadata = {}
                
                integration.metadata["charges_enabled"] = account.get("charges_enabled", False)
                integration.metadata["details_submitted"] = account.get("details_submitted", False)
                integration.metadata["payouts_enabled"] = account.get("payouts_enabled", False)
                integration.last_sync = datetime.now()
                
                db.commit()
                logger.info(f"Updated integration for account: {account_id}")
            
            return {"status": "success", "message": "Account information updated"}
            
        except Exception as e:
            logger.error(f"Error updating integration: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating integration: {str(e)}"
            )
    
    # For other event types, just acknowledge receipt
    logger.info(f"Received event of type {event['type']}, not processing further")
    return {"status": "received", "type": event["type"]}

@router.get("/api/payments", status_code=status.HTTP_200_OK)
async def get_payments(db: Session = Depends(get_db)):
    """
    Get all payments recorded in the system.
    
    Args:
        db: Database session
        
    Returns:
        dict: A list of payment records
    """
    try:
        payments = db.query(Payment).order_by(Payment.timestamp.desc()).all()
        
        result = []
        for payment in payments:
            # Get integration info if this payment is from a connected account
            integration_info = None
            if payment.stripe_account_id:
                integration = db.query(Integration).filter(
                    Integration.account_id == payment.stripe_account_id
                ).first()
                
                if integration:
                    integration_info = {
                        "user_id": integration.user_id,
                        "account_name": integration.account_name
                    }
            
            result.append({
                "id": payment.id,
                "slug": payment.slug,
                "email": payment.email,
                "amount": payment.amount,
                "currency": payment.currency,
                "timestamp": payment.timestamp.isoformat(),
                "dashboard_user_id": payment.dashboard_user_id,
                "stripe_account_id": payment.stripe_account_id,
                "integration": integration_info
            })
        
        return {
            "payments": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error fetching payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payments: {str(e)}"
        ) 