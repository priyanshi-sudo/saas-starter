"""Audit logging — append-only record of who did what in which org."""
from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog

log = logging.getLogger("audit")


async def record(
    session: AsyncSession,
    *,
    org_id: str,
    actor_id: str,
    action: str,
    target: str | None = None,
) -> None:
    entry = AuditLog(
        org_id=org_id,
        actor_id=actor_id,
        action=action,
        target=target,
        created_at=datetime.utcnow(),
    )
    session.add(entry)
    log.info("audit org=%s actor=%s action=%s target=%s", org_id, actor_id, action, target)
