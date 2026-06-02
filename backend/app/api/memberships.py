"""Membership management — list members, invite, change roles."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.core.security import Principal
from app.core.tenant import require_role
from app.models import Invitation, Membership, Organization, Role, User
from app.services import audit, email

router = APIRouter()


class MemberOut(BaseModel):
    user_id: str
    email: str
    role: str


class InviteBody(BaseModel):
    email: str
    role: Role = Role.MEMBER


class RoleChange(BaseModel):
    user_id: str
    role: Role


@router.get("/{org_id}", response_model=list[MemberOut])
async def list_members(
    org_id: str,
    principal: Principal = Depends(require_role("member")),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(Membership, User)
            .join(User, User.id == Membership.user_id)
            .where(Membership.org_id == org_id)
        )
    ).all()
    return [
        MemberOut(user_id=str(m.user_id), email=u.email, role=m.role.value)
        for m, u in rows
    ]


@router.post("/{org_id}/invite")
async def invite(
    org_id: str,
    body: InviteBody,
    principal: Principal = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    org = await session.get(Organization, org_id)
    if org is None:
        raise HTTPException(404, "organization not found")

    invitation = Invitation(org_id=org.id, email=body.email, role=body.role)
    session.add(invitation)
    await audit.record(
        session, org_id=org_id, actor_id=principal.user_id,
        action="member.invited", target=body.email,
    )
    await session.commit()

    link = f"{settings.frontend_url}/invite/{invitation.id}"
    await email.send_invite(body.email, org.name, link)
    return {"invited": body.email, "invitation_id": str(invitation.id)}


@router.post("/{org_id}/role")
async def change_role(
    org_id: str,
    body: RoleChange,
    principal: Principal = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    membership = (
        await session.execute(
            select(Membership).where(
                Membership.org_id == org_id, Membership.user_id == body.user_id
            )
        )
    ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(404, "member not found")

    membership.role = body.role
    await audit.record(
        session, org_id=org_id, actor_id=principal.user_id,
        action="member.role_changed", target=body.user_id,
    )
    await session.commit()
    return {"user_id": body.user_id, "role": body.role.value}
