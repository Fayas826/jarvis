import os
import stripe
from fastapi import APIRouter, Request, HTTPException, Header
import logging

# Ensure STRIPE_API_KEY and STRIPE_WEBHOOK_SECRET are loaded in production .env
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_mock_key")
ENDPOINT_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")

router = APIRouter(prefix="/webhooks/stripe", tags=["Billing"])

@router.post("/")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe Signature")

    payload = await request.body()

    try:
        # Verify the webhook signature to prevent spoofing
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logging.error(f"Stripe Webhook Error (ValueError): {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logging.error(f"Stripe Webhook Error (SignatureVerificationError): {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email')
        
        # Here we would connect to MongoDB to update the user's tier
        # e.g., db.users.update_one({"email": customer_email}, {"$set": {"tier": "L1_PRO"}})
        
        logging.info(f"💰 SUCCESS: Payment received for {customer_email}. Upgrading account to PRO!")

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        
        # e.g., db.users.update_one({"stripe_customer_id": customer_id}, {"$set": {"tier": "L0_FREE"}})
        logging.info(f"📉 ALERT: Subscription canceled for customer {customer_id}. Downgrading to FREE.")

    else:
        logging.info(f"Unhandled Stripe event type: {event['type']}")

    return {"status": "success"}
