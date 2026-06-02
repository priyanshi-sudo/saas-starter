"""Stripe webhook handler — single source of truth for subscription state."""
from __future__ import annotations

import stripe
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.services import billing as billing_service

router = APIRouter()
stripe.api_key = settings.stripe_secret_key


@router.post("/webhook")
async def stripe_webhook(request: Request):
    sig = request.headers.get("stripe-signature")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(400, f"webhook verify failed: {e}")

    handler = {
        "checkout.session.completed": billing_service.on_checkout_complete,
        "customer.subscription.updated": billing_service.on_subscription_updated,
        "customer.subscription.deleted": billing_service.on_subscription_deleted,
        "invoice.payment_failed": billing_service.on_payment_failed,
    }.get(event["type"])

    if handler:
        await handler(event["data"]["object"])
    return {"received": True}


@router.post("/portal")
async def create_portal_session(org_id: str):
    org = await billing_service.get_org_billing(org_id)
    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=f"{settings.frontend_url}/app/{org.slug}/settings/billing",
    )
    return {"url": session.url}
