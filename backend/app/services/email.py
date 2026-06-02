"""Transactional email via Resend.

Falls back to logging when `RESEND_API_KEY` is unset so local/dev runs and
tests don't need a real provider.
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)


async def _send(to: str, subject: str, html: str) -> None:
    if not settings.resend_api_key:
        log.info("[email:dev] to=%s subject=%s", to, subject)
        return
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.email_from,
                "to": [to],
                "subject": subject,
                "html": html,
            },
        )


async def send_invite(to: str, org_name: str, link: str) -> None:
    await _send(
        to,
        f"You've been invited to {org_name}",
        f'<p>Join <b>{org_name}</b>: <a href="{link}">accept invite</a></p>',
    )


async def send_payment_failed(org_id: str) -> None:
    # In a real app, look up the owner's email; the demo logs the event.
    log.warning("payment failed for org %s — owner should be notified", org_id)
    await _send(
        settings.email_from,
        "Payment failed",
        f"<p>Payment failed for organization {org_id}.</p>",
    )
