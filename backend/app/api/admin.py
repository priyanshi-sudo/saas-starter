"""Superadmin panel endpoints.

Gated by a simple allowlist (`ADMIN_EMAILS`) for the demo; a real deployment
would back this with a dedicated superadmin table or claim.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import Principal, current_user
from app.models import AuditLog, Organization

router = APIRouter()

_ADMIN_EMAILS = {
    e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()
}


async def require_superadmin(
    principal: Principal = Depends(current_user),
) -> Principal:
    if principal.email.lower() not in _ADMIN_EMAILS:
        raise HTTPException(403, "superadmin only")
    return principal


@router.get("/orgs")
async def list_all_orgs(
    _: Principal = Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    orgs = (await session.execute(select(Organization))).scalars()
    return [
        {"id": str(o.id), "slug": o.slug, "plan": o.plan, "status": o.status}
        for o in orgs
    ]


@router.get("/orgs/{org_id}/audit")
async def org_audit_log(
    org_id: str,
    _: Principal = Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(AuditLog)
            .where(AuditLog.org_id == org_id)
            .order_by(AuditLog.created_at.desc())
            .limit(100)
        )
    ).scalars()
    return [
        {
            "action": r.action,
            "actor_id": r.actor_id,
            "target": r.target,
            "at": r.created_at.isoformat(),
        }
        for r in rows
    ]
