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
try:
    from app.models.integration import Integration, IntegrationStatus
    INTEGRATION_MODEL_UPDATED = True
except (ImportError, AttributeError):
    INTEGRATION_MODEL_UPDATED = False
    logging.warn("Using legacy Integration model or model not available")

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
    Also processes events from connected accounts when available.
    
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
    
    # If integration model is updated and this is from a connected account, find the dashboard user
    if INTEGRATION_MODEL_UPDATED and account_id:
        logger.info(f"Event from connected account: {account_id}")
        try:
            integration = db.query(Integration).filter(
                Integration.platform == "stripe",
                Integration.account_id == account_id
            ).first()
            
            if integration:
                dashboard_user_id = integration.user_id
                logger.info(f"Found integration for dashboard user: {dashboard_user_id}")
            else:
                logger.warning(f"No integration found for account: {account_id}")
        except Exception as e:
            # If there's an error with the Integration model, log and continue
            logger.error(f"Error finding integration: {e}")
    
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
        
        # For connected accounts, use a default slug if none is provided
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
            # Check if the Payment model has the new columns
            payment_kwargs = {
                "slug": slug,
                "email": email,
                "amount": payment_intent["amount"] / 100,  # Convert from cents to dollars
                "currency": payment_intent["currency"].upper(),
                "timestamp": datetime.fromtimestamp(payment_intent["created"])
            }
            
            # Add the new fields if they're available in the model
            has_new_fields = False
            try:
                # Test if a Payment object can be created with the new fields
                test_payment = Payment(
                    **payment_kwargs,
                    dashboard_user_id=dashboard_user_id,
                    stripe_account_id=account_id
                )
                has_new_fields = True
            except TypeError:
                # If TypeError is raised, the model doesn't have these fields yet
                logger.warning("Payment model doesn't have dashboard_user_id and stripe_account_id fields yet")
                has_new_fields = False
            
            # Create the payment object with the appropriate fields
            if has_new_fields:
                payment = Payment(
                    **payment_kwargs,
                    dashboard_user_id=dashboard_user_id,
                    stripe_account_id=account_id
                )
            else:
                payment = Payment(**payment_kwargs)
            
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
    
    # Handle account.updated events to update integration status if the model is updated
    elif INTEGRATION_MODEL_UPDATED and event["type"] == "account.updated" and account_id:
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
                
                # Update extra_data with additional account information
                if hasattr(integration, 'extra_data') and integration.extra_data is None:
                    integration.extra_data = {}
                
                if hasattr(integration, 'extra_data'):
                    integration.extra_data["charges_enabled"] = account.get("charges_enabled", False)
                    integration.extra_data["details_submitted"] = account.get("details_submitted", False)
                    integration.extra_data["payouts_enabled"] = account.get("payouts_enabled", False)
                
                if hasattr(integration, 'last_sync'):
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
            # Create base payment data
            payment_data = {
                "id": payment.id,
                "slug": payment.slug,
                "email": payment.email,
                "amount": payment.amount,
                "currency": payment.currency,
                "timestamp": payment.timestamp.isoformat(),
            }
            
            # Add new fields if they exist
            if hasattr(payment, 'dashboard_user_id'):
                payment_data["dashboard_user_id"] = payment.dashboard_user_id
            
            if hasattr(payment, 'stripe_account_id'):
                payment_data["stripe_account_id"] = payment.stripe_account_id
                
                # Get integration info if available
                if INTEGRATION_MODEL_UPDATED and payment.stripe_account_id:
                    try:
                        integration = db.query(Integration).filter(
                            Integration.account_id == payment.stripe_account_id
                        ).first()
                        
                        if integration:
                            payment_data["integration"] = {
                                "user_id": integration.user_id,
                                "account_name": integration.account_name
                            }
                    except Exception as e:
                        logger.error(f"Error retrieving integration: {e}")
            
            result.append(payment_data)
        
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