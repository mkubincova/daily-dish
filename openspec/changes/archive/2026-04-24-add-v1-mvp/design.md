# Design — Daily Dish v1 MVP

## Context

Greenfield rebuild of a personal recipe app with two simultaneous goals:

1. **Daily-use product for one user** (the author) — laptop for planning meals
   and prepping shopping lists; phone in the kitchen for cooking instructions.
2. **Portfolio piece** — must demonstrate full-stack work, with Python on the
   backend chosen specifically to differentiate from the author's existing
   JavaScript-only portfolio.

The predecessor (Strapi self-hosted) made daily editing painful, which is the
specific friction this redesign exists to fix.

The author has Vercel, Railway, and Cloudinary accounts already provisioned.

## Goals / Non-Goals

**Goals**
- Pleasant editing experience for the primary user.
- Direct, code-versioned control of schema and data (Alembic migrations).
- A stable, framework-agnostic backend API so future alternative frontends
  (React, Solid, etc.) can consume the same data.
- Strong portfolio signal: modern async Python, typed end-to-end via OpenAPI.
- Public read access for recipes (SEO + sharing); owner-only writes.

**Non-Goals (v1)**
- Multi-tenant collaboration features.
- Recipe discovery beyond chronological listing (no search, no filters, no tags).
- AI-generated recipes or ingredient-based recommendations.
- Mobile native or PWA — responsive web only.
- Image variants beyond what Cloudinary provides on-the-fly.
- Performance optimization beyond reasonable defaults.

## Decisions

### D1. Separated frontend + backend (two deploys)

Frontend Nuxt 3 on Vercel; FastAPI backend + Postgres on Railway.

**Alternatives considered**
- *Nuxt monolithic full-stack* (Nitro server routes for backend logic). Simpler
  to deploy but couples backend to Nuxt and weakens the "API as data product"
  narrative.
- *Next.js + tRPC monolith*. Strong type safety but ties the API to a
  TypeScript client; conflicts with the goal of swapping frontends later.

**Why this**: The author wants to use the backend as a stable data product
across future frontend experiments. Two deploys is more complexity but the
right complexity for the stated goal.

### D2. REST + OpenAPI over GraphQL

REST endpoints; FastAPI emits OpenAPI; the Nuxt frontend generates a typed
client at build time using `openapi-typescript`.

**Alternatives considered**
- *GraphQL via Strawberry*. Would lose FastAPI's auto-OpenAPI on that
  endpoint. Recipe data graph is small and stable; GraphQL's flexibility
  doesn't earn its complexity here.
- *tRPC*. Type-couples the API to a TypeScript client, defeating the
  "frontend-agnostic" goal.

### D3. SQLModel over raw SQLAlchemy 2.0

One class per entity acts as both ORM model and Pydantic schema (with thin
read/write variants when needed).

**Alternatives considered**
- *Raw SQLAlchemy 2.0 + separate Pydantic schemas*. More code, marginally
  stronger résumé phrase, but the duplication slows down a small/medium app.
- *Tortoise ORM*. Async-native but smaller ecosystem and weaker FastAPI
  integration than SQLModel.

**Escape hatch**: SQLModel is SQLAlchemy underneath; complex queries can drop
into raw SQLAlchemy without rewriting models.

### D4. HttpOnly cookie sessions over JWT

OAuth callback lands on the backend, exchanges code with the provider, upserts
the user, sets a signed HttpOnly Secure cookie, and redirects to the frontend.
Subsequent frontend requests include the cookie automatically.

**Alternatives considered**
- *JWT in `Authorization` header*. Stateless, but storing tokens in JS is a
  XSS risk; refresh-token dance adds code; logout is harder.
- *Third-party auth (Auth0, Clerk)*. Overkill for two providers and a
  single-user app; introduces vendor lock-in.

**Cross-origin configuration (decided)**: V1 uses the default Vercel and
Railway domains — no custom domain. The session cookie is therefore set with
`SameSite=None; Secure; HttpOnly`. CORS on the backend allows the Vercel
frontend origin with `allow_credentials=True`. A custom-domain migration
(switching to `SameSite=Lax`) remains a clean option for later.

### D5. Steps as JSONB array; ingredients as a normalized table

Steps live as `JSONB` on `recipes` (objects of `{position, text}` and room to
grow). Ingredients are rows in a separate `ingredients` table with structured
`quantity` / `unit` / `name` columns.

**Alternatives considered**
- *Both as JSON*. Even simpler in v1, but the future "scale to N servings"
  and "find recipes with chicken" features need queryable ingredient
  quantities and names. Migrating later costs more than structuring now.
- *Both as separate tables*. More tables, more join logic. Steps have no
  query patterns worth normalising for.

### D6. UUIDv7 primary keys

Time-orderable, globally unique, no enumeration leakage.

**Alternatives considered**
- *Autoincrement int*. Simpler but leaks count and creation order in URLs.
- *UUIDv4*. Random ordering hurts index locality.

**Implementation note**: Postgres 17 has native UUIDv7. On older versions, use
the `pg_uuidv7` extension or generate in application code.

### D7. Soft delete via `deleted_at`

All recipe queries filter `WHERE deleted_at IS NULL` by default.

**Alternatives considered**
- *Hard delete*. No DB column cost but irreversible for the primary user.
- *No delete (only draft toggle)*. Conflates "I want this gone" with "I want
  this hidden temporarily".

### D8. Cloudinary direct browser upload with backend-signed params

Backend exposes `POST /uploads/sign` which returns timestamp, signature, and
upload params. Browser POSTs directly to Cloudinary's upload endpoint. On
success, frontend PATCHes the recipe with `image_url` + `image_public_id`.

**Alternatives considered**
- *Proxy upload through FastAPI*. Wastes backend bandwidth and Railway egress
  on something Cloudinary handles natively. Slower for the user.
- *Cloudflare R2 / Vercel Blob / Supabase Storage*. Author already has
  Cloudinary configured from the previous app — reusing it is the cheapest
  path. Cloudinary's transformations (resize for thumbs, optimize for mobile)
  are also a fit.

### D9. Public list scope: everyone's public recipes, newest first

Anonymous home page shows all recipes where `is_public AND deleted_at IS NULL`,
ordered by `created_at DESC`.

**Alternatives considered**
- *Only the author's recipes*. Fits "personal cookbook" framing but loses the
  multi-user-ready API surface.
- *Featured / curated*. Premature — no curation mechanism exists.

### D10. `source_url` column reserved on day one

Even though URL import is v2, `recipes.source_url` exists from the first
migration so any imported recipe (or manually noted source) can be tagged
without a future schema change.

**Alternative**: defer the column until URL import lands. Rejected — adding a
nullable column later is fine, but using it consistently from v1 means seed
data and manual entries already carry attribution.

### D11. Monorepo with `apps/api` and `apps/web`

A single repository contains both the FastAPI backend (`apps/api/`) and the
Nuxt frontend (`apps/web/`), with `openspec/`, `docker-compose.yml`, and the
top-level `README.md` at the root. Vercel deploys with root directory set to
`apps/web`; Railway deploys with service root set to `apps/api`.

**Alternatives considered**
- *Two separate repositories*. Cleaner narrative around "stable backend as a
  data product, swappable frontends" but doubles the operational overhead for
  a solo developer (two clones, two PRs to keep in sync, OpenAPI codegen must
  always fetch from the deployed backend, real risk of schema drift between
  unsynchronised commits).

**Why this**: Cross-cutting changes (e.g. add a column → migration +
endpoint + form field) ship as one atomic PR. OpenAPI codegen can read
`apps/api/openapi.json` directly during local dev. Future frontend
experiments (e.g. `apps/web-react/`) live alongside the existing one,
which is a stronger "swap frontends" portfolio story than scattering them
across repos. Extraction to two repos remains possible later via
`git filter-repo` if circumstances change.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Two-deploy ops overhead (CI, env vars, sync) | Single GitHub Actions workflow that triggers both deploys; document env vars in `.env.example` |
| Cookie cross-origin (Vercel ↔ Railway, default domains) | `SameSite=None; Secure; HttpOnly` cookie + CORS `allow_credentials=True`; revisit if/when a custom domain is added |
| OpenAPI ↔ TS client drift between deploys | Generate the client during the frontend build; CI fails if backend OpenAPI is unreachable. Optionally pin a backend OpenAPI snapshot in the frontend repo |
| Cloudinary signed-upload misconfiguration leaks API secret | Secret stays server-side only; never in `NUXT_PUBLIC_*` env. Verify with a "secret not bundled" check in CI |
| SQLModel maturity for complex queries | Acceptable: SQLModel models are SQLAlchemy models; complex queries drop down to `select(...)` directly |
| Solo maintenance + two languages | Accept the cost; dual-language is part of the portfolio narrative |

## Migration Plan

This is a greenfield deploy, not a migration of the old app. The old Strapi
app keeps running in parallel. No automated seed migration is in scope for v1.

Rollback path: the new app is a separate deployment; rolling back means
pointing DNS away from it and continuing to use the old app. No data
migration to undo.

## Open Questions

1. ~~**Custom domain now or later?**~~ **Resolved**: no custom domain in v1.
   Default Vercel + Railway domains; cookie configured `SameSite=None; Secure`.
2. ~~**Monorepo or two repos?**~~ **Resolved**: monorepo with `apps/api` and
   `apps/web`. See decision D11.
3. ~~**Username / display-name editing?**~~ **Resolved**: not in v1. The values
   from the OAuth provider profile are used as-is. Editing is a post-v1 task.
4. ~~**Email visibility?**~~ **Resolved**: a user can see their own email
   (via `/auth/me`); other users' emails are never exposed by the API.
   Public-facing recipe responses identify the owner only by display name
   and avatar URL.
5. ~~**Step images / timers per step?**~~ **Resolved**: not in v1. Each
   recipe has a single cover image only. Steps remain `{position, text}`.
   The JSONB step shape leaves room to add per-step fields later without a
   migration.
