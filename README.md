# SaaS Starter — Multi-tenant Next.js + FastAPI

> Production-leaning SaaS boilerplate. Multi-tenant orgs, role-based access, Stripe subscriptions with seat-based billing, transactional emails, background jobs, and an audit log.

![Stack](https://img.shields.io/badge/Next.js-15-black) ![Stack](https://img.shields.io/badge/FastAPI-0.115-009688) ![Stack](https://img.shields.io/badge/Stripe-billing-635bff) ![Stack](https://img.shields.io/badge/Postgres-16-336791) ![License](https://img.shields.io/badge/license-MIT-green)

## What's inside

| Concern | Solution |
|---|---|
| Auth | Supabase Auth (JWT, RS256) verified against the project JWKS |
| Multi-tenancy | `organizations` + `memberships`, request-scoped via `x-org-id` |
| Authorization | RBAC (`owner` > `admin` > `member`) as a FastAPI dependency |
| Billing | Stripe Checkout + customer portal, seat-count webhooks |
| Emails | Resend wrapper (logs to stdout in dev when no key) |
| Background jobs | Arq + Redis |
| Audit | Append-only `audit_logs` table + superadmin viewer |

## Architecture

```
Browser ──► Next.js (App Router)
               │
        Bearer JWT + x-org-id
               ▼
          FastAPI (REST)
   ┌───────────┼───────────────┐
   ▼           ▼               ▼
Postgres   Stripe API     Redis (Arq worker)
```

The tenant layer (`app/core/tenant.py`) turns a bare authenticated principal into an org-scoped one by loading the caller's membership, so `require_role("admin")` can gate any route.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 15 (App Router), Tailwind CSS |
| Backend | FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Auth | Supabase (JWT via `python-jose`) |
| Billing | `stripe` SDK |
| Jobs | Arq on Redis |
| DB | Postgres 16 |

## Quick start

```bash
cp backend/.env.example backend/.env     # add Stripe + Supabase values
make dev                                  # docker compose: db, redis, api, worker, web
make seed                                 # demo org + 3 users (owner/admin/member)
```

- API: <http://localhost:8000>  ·  Web: <http://localhost:3000>
- Seeded demo creds print to the console.

Local dev (without Docker):

```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# in another shell:
arq app.workers.tasks.WorkerSettings

cd ../frontend && npm install && npm run dev
```

## Configuration

Backend env (`backend/.env`):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Async Postgres DSN |
| `SUPABASE_JWKS_URL` | JWKS endpoint for verifying access tokens |
| `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` | Billing |
| `RESEND_API_KEY` / `EMAIL_FROM` | Transactional email (blank → log to stdout) |
| `REDIS_URL` | Arq broker |
| `ADMIN_EMAILS` | Comma-separated superadmin allowlist for `/api/admin` |
| `FRONTEND_URL` / `CORS_ORIGINS` | URLs |

## API reference

| Method | Path | Role | Description |
|---|---|---|---|
| `GET` | `/health` | — | Liveness |
| `GET` | `/api/auth/me` | auth | Current user (provisions on first login) |
| `POST` | `/api/orgs` | auth | Create org (caller becomes owner) |
| `GET` | `/api/orgs` | auth | List orgs you belong to |
| `GET` | `/api/members/{org_id}` | member | List members |
| `POST` | `/api/members/{org_id}/invite` | admin | Invite by email |
| `POST` | `/api/members/{org_id}/role` | admin | Change a member's role |
| `POST` | `/api/billing/webhook` | Stripe | Subscription state sync |
| `POST` | `/api/billing/portal` | auth | Stripe customer portal link |
| `GET` | `/api/admin/orgs` | superadmin | List all orgs |
| `GET` | `/api/admin/orgs/{id}/audit` | superadmin | Org audit log |

### Stripe webhook events handled

`checkout.session.completed` → activate · `customer.subscription.updated` → sync seats/plan · `customer.subscription.deleted` → downgrade to free · `invoice.payment_failed` → flag past-due + email owner.

## Project structure

```
backend/
  app/
    main.py
    core/
      config.py  db.py
      security.py             # JWT verify, RBAC ordering
      tenant.py               # request-scoped org + require_role()
    api/
      auth.py  organizations.py  memberships.py  billing.py  admin.py
    services/
      billing.py              # Stripe events → DB rows
      email.py                # Resend wrapper
      audit.py                # append-only audit log
    workers/tasks.py          # Arq WorkerSettings
    models/__init__.py        # User/Org/Membership/Invitation/AuditLog
    seed.py                   # demo data
  tests/
  requirements.txt
  Dockerfile
frontend/
  app/
    page.tsx                  # marketing + pricing
    sign-in/page.tsx
    app/page.tsx              # org dashboard
  lib/api.ts  lib/auth.ts
docker-compose.yml
Makefile
```

## Testing

```bash
cd backend && pip install -r requirements.txt && pip install pytest ruff httpx
pytest -q          # health, RBAC ordering, settings parsing, admin allowlist
ruff check app tests
```

## Deployment

- **Backend + worker**: same image (`backend/Dockerfile`), two processes; deploy to Fly.io/Render with managed Postgres + Redis. Configure the Stripe webhook to hit `/api/billing/webhook`.
- **Frontend**: `npm run build` → Vercel.

> Note: organizations/memberships persist in Postgres; the demo uses `init_db()` table creation — wire up Alembic for real migrations before production.

## Roadmap

- [ ] Audit log viewer UI
- [ ] SCIM provisioning for enterprise
- [ ] Usage-based billing meter

## License

MIT — see [LICENSE](LICENSE).
