## Context

The repo is a monorepo with two apps: `apps/api` (FastAPI, deployed to Railway) and `apps/web` (Nuxt 3, deployed to Vercel). Both already work locally. The backend uses Pydantic `Settings` to read environment variables; the frontend uses Nuxt `runtimeConfig`. Neither has deployment configuration files yet, so a first deploy would require guessing build/start commands and re-deriving every env var manually.

## Goals / Non-Goals

**Goals:**

- Provide `railway.toml` so Railway automatically picks up the correct build and start commands for the FastAPI service.
- Provide `vercel.json` so Vercel correctly resolves the monorepo root directory and uses the Nuxt framework preset.
- Provide a `DEPLOYMENT.md` runbook that walks through every external portal (Railway, Vercel, GitHub OAuth, Google OAuth, Cloudinary) and every env var that must be set.
- Ensure `.env.example` files are complete and accurate.

**Non-Goals:**

- CI/CD pipelines or automated preview environments (a v2 concern).
- Custom domains or TLS setup (portal-specific; noted in the runbook but not automated).
- Secrets rotation or secret management tooling.

## Decisions

### 1. `railway.toml` for the API — explicit config over portal UI

**Choice:** Commit a `railway.toml` in `apps/api/` with `[build]` and `[deploy]` sections.

**Why not portal-only config:** UI config is invisible in git, drifts silently, and must be re-entered on every new Railway service. A committed file is the single source of truth.

**Alternative considered:** `Dockerfile` — more portable but overkill for a single-process Python service that `uv` already handles well. Railway's Nixpacks natively supports `uv` if told the install and start commands.

**Key commands:**
- Build: `uv sync --no-dev` (install production deps only).
- Start: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` (Railway injects `$PORT`).
- Migrate on deploy: `uv run alembic upgrade head` wired as a Railway start command prefix (sequential shell chain in the start command, or a separate `[deploy] startCommand`).

### 2. Alembic migration on every deploy

**Choice:** Prepend migration to the start command: `uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

**Why:** Keeps migration and service start atomic per deploy. For a single-developer app with no blue/green strategy this is the simplest approach.

**Alternative considered:** A Railway "pre-deploy" script — not yet widely supported in `railway.toml` v2; chaining in start command is more portable.

**Risk:** If a migration fails the service won't start and Railway will show the error in logs, which is the correct safe behavior.

### 3. `vercel.json` — monorepo root declaration

**Choice:** A minimal `vercel.json` at repo root specifying `"rootDirectory": "apps/web"` and relying on Vercel's auto-detected Nuxt framework preset.

**Why not `apps/web/vercel.json`:** Vercel reads project config from the deployment root; placing it at repo root (with `rootDirectory` pointing into the monorepo) is the documented approach for monorepos.

**Alternative considered:** Vercel CLI `--root` flag or portal-only config — same invisible-in-git problem as Railway portal config.

### 4. `DEPLOYMENT.md` as the runbook

**Choice:** A single `DEPLOYMENT.md` at repo root covering all portals in deploy order.

**Why a doc, not automation:** Portal steps (OAuth app creation, environment variable entry) are one-time human actions that can't be scripted without API tokens. A clear doc is more useful than a half-automated script that still requires manual steps.

**Sections:** Postgres provision → Railway service → Vercel project → GitHub OAuth → Google OAuth → Cloudinary → post-deploy smoke test.

## Risks / Trade-offs

- **`alembic upgrade head` on start is not zero-downtime** — acceptable for a single-user personal app; flagged in the runbook.
- **`railway.toml` `rootDirectory`** — Railway projects that point to `apps/api/` as the service root must have `railway.toml` inside that directory (or specify path in the portal). The runbook must note this.
- **Session cookie cross-origin** — `SameSite=None; Secure` is required when Vercel frontend and Railway backend are on different top-level domains. This is already implemented in `main.py` when `ENVIRONMENT=production`; the runbook must remind the developer to set `ENVIRONMENT=production` on Railway.
