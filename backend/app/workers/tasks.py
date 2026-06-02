"""Background jobs run by Arq.

Start a worker with: `arq app.workers.tasks.WorkerSettings`
"""
from __future__ import annotations

import logging

from arq.connections import RedisSettings

from app.core.config import settings
from app.services import email

log = logging.getLogger(__name__)


async def send_invite_email(ctx: dict, to: str, org_name: str, link: str) -> None:
    await email.send_invite(to, org_name, link)


async def reconcile_seats(ctx: dict, org_id: str) -> None:
    """Placeholder for nightly seat reconciliation against Stripe."""
    log.info("reconciling seats for org %s", org_id)


class WorkerSettings:
    functions = [send_invite_email, reconcile_seats]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
