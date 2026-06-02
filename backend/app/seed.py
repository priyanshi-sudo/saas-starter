"""Seed demo data: one org, three users, one membership each.

Run with `python -m app.seed` (or `make seed`) once Postgres is up.
"""
from __future__ import annotations

import asyncio
import uuid

from app.core.db import async_session, init_db
from app.models import Membership, Organization, Role, User

DEMO = [
    ("owner@demo.test", "Olivia Owner", Role.OWNER),
    ("admin@demo.test", "Aiden Admin", Role.ADMIN),
    ("member@demo.test", "Maya Member", Role.MEMBER),
]


async def main() -> None:
    await init_db()
    async with async_session() as session:
        org = Organization(id=uuid.uuid4(), name="Demo Inc", slug="demo", plan="pro")
        session.add(org)
        await session.flush()

        for email_addr, name, role in DEMO:
            user = User(id=uuid.uuid4(), email=email_addr, name=name)
            session.add(user)
            await session.flush()
            session.add(Membership(org_id=org.id, user_id=user.id, role=role))

        await session.commit()

    print("Seeded org 'demo' with users:")
    for email_addr, _, role in DEMO:
        print(f"  {email_addr}  ({role.value})")


if __name__ == "__main__":
    asyncio.run(main())
