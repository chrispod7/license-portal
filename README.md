# License Management Portal

A full-stack app for issuing, validating, and revoking software license keys.

**Stack:** React (Vite) · FastAPI · SQLAlchemy 2 + Alembic · PostgreSQL · Docker Compose · GitHub Actions

## Quick start

```bash
docker compose up --build
```

| URL | What |
| --- | --- |
| http://localhost:8080 | Web UI |
| http://localhost:8080/api/docs | Interactive API docs (Swagger) |
| http://localhost:8000 | API directly |

Set `LICENSE_SIGNING_SECRET` in your environment (or a `.env` file) before running anywhere but your laptop.

## Data model

```
users ──< licenses >── products
```

| Table | Key columns |
| --- | --- |
| `users` | `id`, `email` (unique), `full_name`, `created_at` |
| `products` | `id`, `sku` (unique), `name`, `description`, `created_at` |
| `licenses` | `id`, `key` (unique), `user_id` → users, `product_id` → products, `status` (`active`/`revoked`), `issued_at`, `expires_at`, `revoked_at`, `revoke_reason` |

- Foreign keys are `ON DELETE RESTRICT`: you can't delete a user or product that still has licenses, so revocation history is never lost.
- "Expired" isn't stored. It's derived from `expires_at` at read time, so there's no cron job and no stale status.
- The schema is managed with Alembic migrations (`backend/alembic/versions`), applied automatically when the backend container starts.

## License keys

Format: `SKU-XXXXX-XXXXX-XXXXX-CCCCC`

- Three random groups use a Crockford-style alphabet (no `I`, `L`, `O`, `U`) drawn from `secrets`.
- The last group is an HMAC-SHA256 checksum of the SKU and random part, signed with `LICENSE_SIGNING_SECRET`.
- Validation checks the format and checksum **before** touching the database, so typos and forged keys are rejected cheaply. The database stays the source of truth for revocation and expiry.

## REST API

All routes are under `/api`.

| Method | Path | Description |
| --- | --- | --- |
| GET / POST | `/users` | List / create users |
| GET / PATCH / DELETE | `/users/{id}` | Read / update / delete a user |
| GET / POST | `/products` | List / create products |
| GET / PATCH / DELETE | `/products/{id}` | Read / update / delete a product (SKU is immutable) |
| GET | `/licenses?user_id=&product_id=&status=` | List licenses with optional filters |
| POST | `/licenses` | Issue a license `{user_id, product_id, expires_at?}` |
| GET | `/licenses/{id}` | Read a license |
| POST | `/licenses/{id}/revoke` | Revoke `{reason?}` |
| POST | `/licenses/validate` | Validate `{key, sku?}` → `{valid, reason}` |

`validate` always returns 200; `reason` is one of `malformed`, `not_found`, `wrong_product`, `revoked`, `expired`.

## Tests

**Backend:** unit tests (key generation and validation rules, no DB) plus integration tests (the real API against PostgreSQL).

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/unit
# needs Postgres: docker compose up -d db
DATABASE_URL=postgresql+psycopg://license:license@localhost:5432/license_portal pytest tests/integration
```

> Integration tests drop and recreate the tables in the database they point at. Use a throwaway database.

**Frontend:** Vitest + React Testing Library.

```bash
cd frontend
npm ci
npm test
```

## CI

`.github/workflows/ci.yml` runs on every push and PR:

1. **backend**: ruff lint → unit tests → Alembic upgrade/downgrade check → integration tests against a Postgres service container
2. **frontend**: `npm ci` → tests → production build
3. **docker**: builds the images, starts the stack, and smoke-tests `/api/health` through nginx

## Local development without Docker

```bash
docker compose up -d db
cd backend && alembic upgrade head && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev   # http://localhost:5173, proxies /api to :8000
```

## Project layout

```
backend/
  app/
    main.py          FastAPI app, error handlers, router wiring
    models.py        SQLAlchemy models
    schemas.py       Pydantic request/response models
    keys.py          Key generation and checksum
    services.py      Issue / revoke / validate business rules
    routers/         users, products, licenses
  alembic/           Migrations
  tests/unit/        Pure-logic tests
  tests/integration/ API + Postgres tests
frontend/
  src/api.js         Fetch wrapper
  src/components/    Licenses, Validate, Products, Users panels
  nginx.conf         Serves the SPA and proxies /api to the backend
```

## Possible next steps

- Authentication for admin routes (e.g. OAuth2 + JWT), with `validate` left public or protected by a per-product API key
- Activation tracking (seat limits per license, machine fingerprints)
- Audit log table for issue/revoke events
- Pagination on list endpoints
