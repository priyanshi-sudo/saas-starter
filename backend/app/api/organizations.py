"""Organization endpoints — create an org, list the ones you belong to."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_or_create_user
from app.core.db import get_session
from app.core.security import Principal, current_user
from app.models import Membership, Organization, Role
from app.services import audit

router = APIRouter()


class OrgCreate(BaseModel):
    name: str
    slug: str


class OrgOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    role: str | None = None


@router.post("", response_model=OrgOut)
async def create_org(
    body: OrgCreate,
    principal: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, principal)

    exists = (
        await session.execute(select(Organization).where(Organization.slug == body.slug))
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "slug already taken")

    org = Organization(name=body.name, slug=body.slug)
    session.add(org)
    await session.flush()
    session.add(Membership(org_id=org.id, user_id=user.id, role=Role.OWNER))
    await audit.record(
        session, org_id=str(org.id), actor_id=str(user.id), action="org.created"
    )
    await session.commit()
    return OrgOut(
        id=str(org.id), name=org.name, slug=org.slug, plan=org.plan, role="owner"
    )


@router.get("", response_model=list[OrgOut])
async def list_my_orgs(
    principal: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(Organization, Membership.role)
            .join(Membership, Membership.org_id == Organization.id)
            .where(Membership.user_id == principal.user_id)
        )
    ).all()
    return [
        OrgOut(
            id=str(o.id), name=o.name, slug=o.slug, plan=o.plan, role=role.value
        )
        for o, role in rows
    ]
