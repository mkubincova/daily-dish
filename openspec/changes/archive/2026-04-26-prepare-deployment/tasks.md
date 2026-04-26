## 1. Railway API Configuration

- [x] 1.1 Create `apps/api/railway.toml` with build command (`uv sync --no-dev`), start command (`uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`), and health check path (`/health`)
- [x] 1.2 Verify `apps/api/.env.example` covers every field in `app/config.py` Settings, adding any missing entries with comments

## 2. Vercel Frontend Configuration

- [x] 2.1 Create `vercel.json` at repo root declaring `rootDirectory: apps/web` and `framework: nuxtjs`
- [x] 2.2 Verify `apps/web/.env.example` covers every runtimeConfig key in `nuxt.config.ts`, adding any missing entries with comments

## 3. Deployment Runbook

- [x] 3.1 Create `DEPLOYMENT.md` at repo root with sections: Prerequisites, Railway (Postgres + API service + env vars), Vercel (project setup + env vars), GitHub OAuth app setup, Google OAuth app setup, Cloudinary setup, Post-deploy smoke test
- [x] 3.2 Include exact OAuth callback URL patterns for both providers (`/auth/github/callback`, `/auth/google/callback`)
- [x] 3.3 Call out `ENVIRONMENT=production` requirement and its session cookie (SameSite=None) implication in the Railway env var section
