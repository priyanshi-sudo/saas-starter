"""JWT verification + RBAC decorators."""
from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable

import httpx
from fastapi import Depends, HTTPException, Request, status
from jose import jwt
from pydantic import BaseModel

from app.core.config import settings

_JWKS_CACHE: dict | None = None
ROLES_ORDER = {"member": 0, "admin": 1, "owner": 2}


class Principal(BaseModel):
    user_id: str
    email: str
    org_id: str | None = None
    role: str | None = None


async def _jwks() -> dict:
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        async with httpx.AsyncClient() as c:
            _JWKS_CACHE = (await c.get(settings.supabase_jwks_url)).json()
    return _JWKS_CACHE


async def current_user(request: Request) -> Principal:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer")
    token = auth.split(" ", 1)[1]
    try:
        claims = jwt.decode(
            token,
            await _jwks(),
            algorithms=["RS256"],
            audience="authenticated",
        )
    except jwt.JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"bad token: {e}")

    return Principal(
        user_id=claims["sub"],
        email=claims["email"],
        org_id=request.headers.get("x-org-id"),
    )


def require_role(min_role: str) -> Callable:
    """Decorator: ensure the principal has at least `min_role` in the org."""

    def decorator(fn: Callable[..., Awaitable]):
        @wraps(fn)
        async def wrapper(*args, principal: Principal = Depends(current_user), **kw):
            if principal.role is None or ROLES_ORDER[principal.role] < ROLES_ORDER[min_role]:
                raise HTTPException(403, f"requires {min_role} or higher")
            return await fn(*args, principal=principal, **kw)

        return wrapper

    return decorator
