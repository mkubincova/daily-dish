# Tasks — add-v1-mvp

## 1. Project setup

- [x] 1.1 Create monorepo layout: `apps/api/` (FastAPI), `apps/web/` (Nuxt), with `openspec/`, `docker-compose.yml`, and root `README.md` at the top level
- [x] 1.2 Initialise FastAPI project with `uv init`, add baseline deps (`fastapi`, `uvicorn`, `sqlmodel`, `alembic`, `authlib`, `python-jose`, `cloudinary`, `httpx`)
- [x] 1.3 Initialise Nuxt 3 project with `npx nuxi init`, add Pinia, Tailwind, `openapi-typescript`
- [x] 1.4 Add Ruff config + pre-commit hook for the API
- [x] 1.5 Add Biome (or ESLint+Prettier) for the web app
- [x] 1.6 Add `docker-compose.yml` with Postgres 16 service for local dev
- [x] 1.7 Set up `.env.example` files for both apps documenting every required variable
- [x] 1.8 Create GitHub Actions workflow that runs API lint+tests and web lint+tests on PR

## 2. Database schema and migrations

- [x] 2.1 Configure Alembic with async engine, env.py wired to settings
- [x] 2.2 Define SQLModel `User` (id UUIDv7, email, name, avatar_url, provider, provider_id, created_at, updated_at; unique on `(provider, provider_id)`)
- [x] 2.3 Define SQLModel `Recipe` (id UUIDv7, user_id FK, title, slug unique, description, image_url, image_public_id, source_url, servings, prep_time_minutes, cook_time_minutes, steps JSONB, is_public, deleted_at, created_at, updated_at)
- [x] 2.4 Define SQLModel `Ingredient` (id, recipe_id FK, position, quantity, unit, name, notes)
- [x] 2.5 Generate initial Alembic migration including partial indexes (`recipes_public_feed_idx`, `recipes_owner_idx`, `recipes_slug_idx`, `ingredients_recipe_pos_idx`)
- [x] 2.6 Add UUIDv7 generation strategy (Postgres 17 native, `pg_uuidv7` extension, or app-side library)
- [x] 2.7 Add slugify utility with random suffix and unit tests
- [x] 2.8 Confirm `make db-up`, `make db-migrate`, `make db-reset` developer commands work

## 3. Auth (backend)

- [x] 3.1 Register Authlib OAuth client for GitHub
- [x] 3.2 Register Authlib OAuth client for Google
- [x] 3.3 Implement `/auth/{provider}/login` redirect endpoint
- [x] 3.4 Implement `/auth/{provider}/callback` endpoint (token exchange, user upsert, cookie set, redirect)
- [x] 3.5 Implement signed-cookie session backend (HttpOnly, Secure, SameSite per environment)
- [x] 3.6 Implement `get_current_user` dependency for FastAPI route protection
- [x] 3.7 Implement `/auth/me` returning the current user or 401
- [x] 3.8 Implement `/auth/logout` clearing the cookie
- [x] 3.9 Add CORS middleware allowing the frontend origin with `allow_credentials=True`
- [x] 3.10 Add tests covering the upsert, cookie set/clear, tamper rejection, and 401/404 flows

## 4. Recipes API

- [x] 4.1 `POST /recipes` (auth required) — create with structured ingredients and steps
- [x] 4.2 `PATCH /recipes/{id}` (owner only, returns 404 for non-owners) — full or partial update incl. ingredients/steps replacement
- [x] 4.3 `DELETE /recipes/{id}` (owner only) — soft delete
- [x] 4.4 `GET /recipes/{slug}` — public if `is_public`, owner-only otherwise, 404 on draft for non-owners
- [x] 4.5 `GET /recipes` — public list, paginated, ordered by `created_at` desc, excludes drafts and deleted
- [x] 4.6 `GET /recipes/mine` (auth required) — owner's recipes including drafts
- [x] 4.7 Pagination strategy (cursor or offset+limit) with sensible default page size
- [x] 4.8 Tests covering all six endpoints across owner / non-owner / anonymous and public / draft / deleted

## 5. Image upload (Cloudinary)

- [x] 5.1 Add Cloudinary config from env vars (cloud name, api key, api secret)
- [x] 5.2 `POST /uploads/sign` (auth required) — return signed upload params
- [x] 5.3 Store `image_url` + `image_public_id` on recipe create/update
- [x] 5.4 Add CI check that Cloudinary secret never appears in frontend bundle
- [x] 5.5 Tests for sign endpoint (auth required; signature valid)

## 6. OpenAPI client generation

- [x] 6.1 Confirm FastAPI `/openapi.json` shape and tagging is sane
- [x] 6.2 Add `openapi-typescript` script in the web app to fetch and codegen the typed client
- [x] 6.3 Wire codegen into the web build pipeline; CI fails if generation fails
- [x] 6.4 Pin the generated client output as a tracked file in the repo for reviewability

## 7. Frontend skeleton

- [x] 7.1 Set up Tailwind, base layout, header with conditional sign-in/sign-out button
- [x] 7.2 Configure `useFetch`/Pinia for API calls with `credentials: 'include'`
- [x] 7.3 Implement auth store backed by `/auth/me` (call on app mount, refresh on sign-in)
- [x] 7.4 Add sign-in buttons (GitHub + Google) that hit backend OAuth login URLs
- [x] 7.5 Add sign-out action calling backend `/auth/logout`
- [x] 7.6 Add basic 404 + error page

## 8. Frontend pages

- [x] 8.1 `/` — public recipe list (SSR), card grid with image, title, description, owner name
- [x] 8.2 `/r/[slug]` — recipe detail page (SSR), shows ingredients (ordered) and steps (ordered)
- [x] 8.3 Owner-only Edit/Delete buttons on detail page
- [x] 8.4 `/me` — owner's recipe list including drafts (client-only or SSR with cookie)
- [x] 8.5 `/r/new` — recipe form (client-only)
- [x] 8.6 `/r/[slug]/edit` — recipe edit form, prefilled
- [x] 8.7 Recipe form: dynamic ingredients rows (qty / unit / name / notes / reorder)
- [x] 8.8 Recipe form: dynamic steps with reorder
- [x] 8.9 Recipe form: Cloudinary upload widget (or custom dropzone) using signed params from API
- [x] 8.10 Recipe form: `is_public` toggle, prep/cook time inputs, servings input, source URL input
- [x] 8.11 Soft delete confirmation dialog
- [x] 8.12 Mobile-friendly detail view (cooking-on-phone use case): generous spacing, large text, scroll-friendly

## 9. Documentation

- [x] 9.1 Write top-level `README.md`: what Daily Dish is, links to live site, brief stack overview, link to OpenSpec
- [x] 9.2 Write `apps/api/README.md`: dev setup, migrations, OAuth env vars, Cloudinary setup
- [x] 9.3 Write `apps/web/README.md`: dev setup, codegen step, env vars
- [x] 9.4 Capture portfolio-relevant decisions in the project README (link to `openspec/changes/add-v1-mvp/design.md`)
