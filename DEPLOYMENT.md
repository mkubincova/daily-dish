# Deployment Guide

Step-by-step instructions for a first-time production deploy of Daily Dish.

**Architecture:** `apps/api` → Railway (FastAPI + Postgres) · `apps/web` → Vercel (Nuxt 3)

---

## Prerequisites

Accounts that must exist before you start:

| Account | Used for |
|---|---|
| [Railway](https://railway.app) | API service + managed Postgres |
| [Vercel](https://vercel.com) | Nuxt frontend |
| [GitHub](https://github.com/settings/developers) | OAuth login |
| [Google Cloud Console](https://console.cloud.google.com) | OAuth login |
| [Cloudinary](https://cloudinary.com) | Recipe image storage |

---

## 1. Railway — Postgres

1. In your Railway project, click **New Service → Database → PostgreSQL**.
2. No URL copying needed — the API service will reference Postgres via Railway's internal network using variable references (see step 2a).

---

## 2. Railway — API Service

1. Click **New Service → GitHub Repo**, select this repository.
2. Set the **Root Directory** to `apps/api` (Railway will find `railway.toml` there automatically).
3. Railway will auto-detect the build and start commands from `apps/api/railway.toml`.
   - Build: `uv sync --no-dev`
   - Start: `uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Alembic runs migrations before the server starts on every deploy.

### 2a. Railway environment variables

Set the following in the Railway service's **Variables** tab:

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://${{ Postgres.PGUSER }}:${{ Postgres.PGPASSWORD }}@${{ Postgres.PGHOST }}:${{ Postgres.PGPORT }}/${{ Postgres.PGDATABASE }}` | Uses Railway's internal network — faster, no egress, auto-updates if credentials rotate |
| `SECRET_KEY` | _(random 64-char hex)_ | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FRONTEND_URL` | `https://<your-vercel-domain>` | Your Vercel deployment URL (e.g. `https://daily-dish.vercel.app`); set this after Vercel is deployed |
| `ENVIRONMENT` | `production` | **Required.** This enables `SameSite=None; Secure` on session cookies — without it the Vercel frontend cannot authenticate across origins |
| `GITHUB_CLIENT_ID` | _(from step 4)_ | |
| `GITHUB_CLIENT_SECRET` | _(from step 4)_ | |
| `GOOGLE_CLIENT_ID` | _(from step 5)_ | |
| `GOOGLE_CLIENT_SECRET` | _(from step 5)_ | |
| `CLOUDINARY_CLOUD_NAME` | _(from step 6)_ | |
| `CLOUDINARY_API_KEY` | _(from step 6)_ | |
| `CLOUDINARY_API_SECRET` | _(from step 6)_ | |

> **Session cookie note:** When the Vercel frontend (`https://daily-dish.vercel.app`) and the Railway API (`https://daily-dish-api.up.railway.app`) are on different domains, the browser requires `SameSite=None; Secure` for the session cookie to be sent cross-origin. `ENVIRONMENT=production` activates this in `apps/api/app/main.py`. If you later configure a custom domain so both apps share a common parent (e.g. `app.yourdomain.com` and `api.yourdomain.com`), you can switch to `SameSite=Lax`.

---

## 3. Vercel — Frontend

1. In Vercel, click **Add New Project → Import Git Repository**, select this repository.
2. In the **Configure Project** screen (before deploying), expand **Root Directory** and set it to `apps/web`. This is required — Vercel cannot detect it automatically from a monorepo.
3. Vercel auto-detects the Nuxt framework once the root directory is set.

### 3a. Vercel environment variables

Set the following in **Project Settings → Environment Variables**:

| Variable | Value | Notes |
|---|---|---|
| `NUXT_PUBLIC_API_URL` | `https://<your-railway-domain>` | Your Railway API URL, no trailing slash |

> The Vercel domain (needed for `FRONTEND_URL` in Railway step 2a) is shown after the first successful Vercel deploy. Go back and update `FRONTEND_URL` in Railway once you have it.

---

## 4. GitHub OAuth App

1. Go to **GitHub → Settings → Developer Settings → OAuth Apps → New OAuth App**.
2. Fill in:
   - **Application name:** Daily Dish
   - **Homepage URL:** `https://<your-vercel-domain>`
   - **Authorization callback URL:** `https://<your-railway-domain>/auth/github/callback`
3. After creating, copy **Client ID** and generate a **Client Secret**.
4. Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in Railway (step 2a).

---

## 5. Google OAuth App

1. Go to [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
2. Choose **Web application**.
3. Under **Authorized redirect URIs**, add:
   - `https://<your-railway-domain>/auth/google/callback`
4. Copy **Client ID** and **Client Secret**.
5. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in Railway (step 2a).

> If prompted, configure the **OAuth consent screen** first. For a personal app, **External** user type and `mkubincova@proton.me` as a test user is sufficient without publishing.

---

## 6. Cloudinary

1. Log in to [Cloudinary](https://cloudinary.com/console).
2. From the dashboard, copy:
   - **Cloud name**
   - **API Key**
   - **API Secret**
3. Set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` in Railway (step 2a).

The existing Cloudinary account from the predecessor app can be reused — images are namespaced by `public_id` and won't conflict.

---

## 7. Post-Deploy Smoke Test

After all env vars are set and both services are deployed:

- [ ] `GET https://<railway-domain>/health` returns `{"status": "ok"}`
- [ ] `GET https://<railway-domain>/docs` loads the FastAPI Swagger UI
- [ ] `https://<vercel-domain>` loads the Daily Dish homepage
- [ ] Click **Sign in with GitHub** → completes OAuth flow → user is logged in
- [ ] Click **Sign in with Google** → completes OAuth flow → user is logged in
- [ ] Create a recipe with an image → image uploads to Cloudinary and appears in the recipe
- [ ] Recipe list page loads correctly after login

---

## Redeploy & Rollback

- **Redeploy:** Push to `main`. Railway and Vercel both auto-deploy on push.
- **Migrations:** `alembic upgrade head` runs automatically on every Railway deploy start. If a migration fails, Railway will not start the new instance and will show the error in the deploy logs.
- **Rollback:** Use Railway's **Deployments** tab to re-deploy a previous release. Run `uv run alembic downgrade -1` manually via Railway's **Shell** tab if the new migration needs to be undone first.
