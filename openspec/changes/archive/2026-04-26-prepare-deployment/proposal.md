## Why

The app is functionally complete but has no deployment configuration files and no runbook for setting up the required third-party portals (Railway, Vercel, GitHub OAuth, Google OAuth, Cloudinary). Without these, going live requires re-deriving every setting from scratch.

## What Changes

- Add `railway.toml` to `apps/api/` so Railway knows how to build and start the FastAPI service.
- Add Alembic migration step wired into the Railway deploy process (run-on-deploy).
- Add `vercel.json` to `apps/web/` (or repo root) to declare the monorepo root directory and Nuxt framework preset.
- Add `DEPLOYMENT.md` at the repo root — a step-by-step runbook covering every portal (Railway, Vercel, GitHub OAuth, Google OAuth, Cloudinary), every environment variable, and every redirect URI/CORS origin that must be configured.
- Verify `.env.example` files are complete and match the live `Settings` model.

## Capabilities

### New Capabilities

- `deployment-config`: Deployment configuration files (`railway.toml`, `vercel.json`) and a developer runbook (`DEPLOYMENT.md`) that makes first-deploy fully self-contained.

### Modified Capabilities

_(none — no existing spec-level behavior changes)_

## Impact

- **`apps/api/`**: new `railway.toml`; no code changes.
- **`apps/web/`**: new or updated `vercel.json`; no code changes.
- **Repo root**: new `DEPLOYMENT.md`.
- **`.env.example` files**: may need minor additions if any setting is missing.
- No API contract changes, no migrations, no dependency additions.
