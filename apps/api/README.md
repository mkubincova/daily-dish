# Daily Dish API

FastAPI backend for the Daily Dish recipe app.

## Dev setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker

```bash
# 1. Clone & navigate
cd apps/api

# 2. Copy env and fill in values
cp .env.example .env

# 3. Install dependencies
uv sync --all-groups

# 4. Start local Postgres
make db-up

# 5. Run migrations
make db-migrate

# 6. Start server (http://localhost:8000)
make dev
```

OpenAPI docs at `http://localhost:8000/docs`.

## Migrations

```bash
make db-migrate          # apply all pending migrations
make db-reset            # wipe and re-run from scratch

# Create a new migration after model changes:
uv run alembic revision --autogenerate -m "describe change"
```

## OAuth setup

### GitHub
1. Go to https://github.com/settings/developers → New OAuth App
2. Set callback URL to `http://localhost:8000/auth/github/callback` (dev) and your production URL
3. Copy client ID + secret into `.env`

### Google
1. Go to https://console.cloud.google.com/ → APIs & Services → Credentials
2. Create OAuth 2.0 client, set redirect URI to `http://localhost:8000/auth/google/callback`
3. Copy client ID + secret into `.env`

## Cloudinary setup

1. Sign in at https://cloudinary.com/console
2. Copy cloud name, API key, and API secret into `.env`
3. The backend signs upload params; images are uploaded directly from the browser

## Tests

```bash
make test
# or
uv run pytest
```

## Linting

```bash
make lint
# or
uv run ruff check app/ tests/ && uv run ruff format --check app/ tests/
```

## Deployment (Railway)

- Build command: `uv sync`
- Start command: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set all env vars from `.env.example` in the Railway dashboard
- Run `uv run alembic upgrade head` as a one-off command after provisioning the DB
