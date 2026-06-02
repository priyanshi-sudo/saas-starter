"""Auth-adjacent endpoints — who am I, and provisioning on first login."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import Principal, current_user
from app.models import User

router = APIRouter()


async def get_or_create_user(session: AsyncSession, principal: Principal) -> User:
    """Mirror the Supabase user into our DB the first time we see them."""
    user = await session.get(User, principal.user_id)
    if user is None:
        user = User(id=principal.user_id, email=principal.email)
        session.add(user)
        await session.flush()
    return user


@router.get("/me")
async def me(
    principal: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    user = await get_or_create_user(session, principal)
    await session.commit()
    return {"id": str(user.id), "email": user.email, "name": user.name}
