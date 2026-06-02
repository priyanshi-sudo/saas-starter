"""Subscription state syncing — Stripe events become DB rows here."""
from __future__ import annotations

from sqlalchemy import select

from app.core.db import async_session
from app.models import Organization
from app.services.email import send_payment_failed


async def get_org_billing(org_id: str) -> Organization:
    async with async_session() as s:
        return (await s.execute(select(Organization).where(Organization.id == org_id))).scalar_one()


async def on_checkout_complete(session: dict):
    org_id = session["metadata"]["org_id"]
    async with async_session() as s:
        org = (await s.execute(select(Organization).where(Organization.id == org_id))).scalar_one()
        org.stripe_customer_id = session["customer"]
        org.stripe_subscription_id = session["subscription"]
        org.plan = session["metadata"].get("plan", "pro")
        org.status = "active"
        await s.commit()


async def on_subscription_updated(sub: dict):
    async with async_session() as s:
        org = (
            await s.execute(
                select(Organization).where(Organization.stripe_subscription_id == sub["id"])
            )
        ).scalar_one()
        org.seat_count = sub["items"]["data"][0]["quantity"]
        org.plan = sub["items"]["data"][0]["price"]["nickname"] or org.plan
        org.status = sub["status"]
        await s.commit()


async def on_subscription_deleted(sub: dict):
    async with async_session() as s:
        org = (
            await s.execute(
                select(Organization).where(Organization.stripe_subscription_id == sub["id"])
            )
        ).scalar_one()
        org.plan = "free"
        org.status = "cancelled"
        await s.commit()


async def on_payment_failed(invoice: dict):
    async with async_session() as s:
        org = (
            await s.execute(
                select(Organization).where(Organization.stripe_customer_id == invoice["customer"])
            )
        ).scalar_one()
        org.status = "past_due"
        await s.commit()
    await send_payment_failed(org_id=str(org.id))
