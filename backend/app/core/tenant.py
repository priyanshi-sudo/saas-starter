"""Request-scoped tenant context.

Turns a bare authenticated principal into an org-scoped one by loading the
caller's membership (and therefore their role) for the `x-org-id` header.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import ROLES_ORDER, Principal, current_user
from app.models import Membership


async def get_principal(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Principal:
    principal = await current_user(request)
    if principal.org_id:
        membership = (
            await session.execute(
                select(Membership).where(
                    Membership.org_id == principal.org_id,
                    Membership.user_id == principal.user_id,
                )
            )
        ).scalar_one_or_none()
        if membership is None:
            raise HTTPException(403, "not a member of this organization")
        principal.role = membership.role.value
    return principal


def require_role(min_role: str):
    """Dependency factory enforcing a minimum role in the current org."""

    async def _dep(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role is None or ROLES_ORDER[principal.role] < ROLES_ORDER[min_role]:
            raise HTTPException(403, f"requires {min_role} or higher")
        return principal

    return _dep
