# Bootstrap the Daily Dish v1 MVP

## Why

The author maintains a personal recipe collection in a self-hosted Strapi app
that doubles as CMS and database. Editing recipes through the Strapi admin UI
became impractical for the primary user (the author) — bulk edits are awkward,
schema changes mean clicking through admin forms, and there is no clean
scripted path for imports. The existing app cannot be incrementally rescued
without reproducing the same friction.

The rebuild also serves as a portfolio piece. The author's existing portfolio
is JavaScript-only; deliberately introducing a Python backend (FastAPI) adds a
distinct, hireable signal. This change establishes the v1 MVP that future
features (filtering, favorites, URL-import, AI suggestions, mobile PWA) will
extend.

## What Changes

- Stand up a new web application from scratch with separated frontend and backend.
- Provide OAuth sign-in via GitHub and Google, with cookie-based sessions.
- Allow signed-in users to create, edit, soft-delete, and toggle public/draft
  visibility on recipes they own.
- Allow anyone (signed in or not) to browse public recipes in reverse-
  chronological order and view individual recipe detail pages.
- Persist recipes with structured ingredients (quantity / unit / name) and
  ordered steps stored as a JSONB array.
- Reserve a `source_url` column on recipes from day one to support future
  URL-import without migration.
- Integrate Cloudinary for hero images via direct browser upload using
  backend-signed parameters.
- Publish a typed REST API (FastAPI auto-generated OpenAPI) consumable by the
  Nuxt frontend through `openapi-typescript`, and by future alternative
  frontends without changes to the backend.

## Capabilities

### New Capabilities
- `auth`: OAuth (GitHub + Google) sign-in, session management via HttpOnly
  cookies, and owner-based authorization for recipe write operations. Public
  read access requires no authentication.
- `recipes`: CRUD for recipes including structured ingredients, JSONB step
  arrays, public/draft visibility, soft delete, public chronological listing,
  owner listing (including drafts), and Cloudinary-backed image upload via
  signed parameters.

### Modified Capabilities
None. Greenfield project — no existing specs to amend.

## Impact

**New artifacts**
- Nuxt 3 frontend application (Vercel deployment).
- FastAPI backend application (Railway deployment).
- PostgreSQL database (Railway).
- Alembic migration baseline.
- OpenAPI schema published at `/openapi.json` and consumed by the frontend at build time.

**New external integrations**
- GitHub OAuth app (to be created).
- Google OAuth client (to be created).
- Cloudinary account (existing, carried over from the predecessor app).

**New tooling**
- `uv` (Python package management), `Ruff` (lint/format), `Alembic` (migrations).
- `openapi-typescript` (typed API client generation).
- `docker-compose` for local Postgres during development.

**Out of scope for this change** (kept here for v2+ planning)
- Tags / categories / filtering.
- Saving other users' recipes as favorites.
- URL import from third-party sites.
- Recipe scaling (adjust servings).
- AI features (e.g. "what can I cook with these ingredients").
- PWA / offline support.

**Continuity with the predecessor app**
- The old Strapi-based app remains live and is **not** migrated in place.
  Schema decisions are not constrained by the old shape.
