# Daily Dish

Personal recipe app + portfolio project. Single developer, single primary user (the author). Used on laptop for planning and on phone in the kitchen for cooking.

## Tech stack

- **Frontend:** Nuxt 3 (Vue 3, SSR), Pinia, Tailwind. Vitest + Playwright. Deployed on Vercel.
- **Backend:** FastAPI (Python 3.12+), SQLModel, Pydantic v2, async. `uv` for packages, Ruff for lint/format, Pytest + httpx for tests. Deployed on Railway.
- **DB:** Postgres (Railway) + Alembic migrations. `docker-compose` for local Postgres.
- **Auth:** OAuth (GitHub + Google) via Authlib → HttpOnly `SameSite=Lax; Secure` session cookies. Browser traffic routes through the Nuxt proxy at `/api/**` so cookies are always first-party (same Vercel origin); privacy-strict browsers work correctly.
- **Images:** Cloudinary — backend signs params, browser uploads direct. Store both `image_url` and `image_public_id`.
- **API:** REST. FastAPI's OpenAPI → typed client via `openapi-typescript` at build time.

## Architecture — non-negotiables

- **Separate FE + BE deploys.** Backend is a stable "data product"; do not collapse into a Nuxt monolith.
- **REST, not GraphQL/tRPC.** Preserves OpenAPI + multi-frontend consumability.
- **SQLModel over raw SQLAlchemy 2.0.** Drop to plain SQLAlchemy only when a query demands it.
- **Recipe shape:** steps = JSONB array on `recipes`; ingredients = their own normalized table.
- **UUIDv7** primary keys. **Soft delete** via `deleted_at` — never hard-delete recipes.
- `is_public` on recipes (default true). `source_url` column reserved from day one for future URL-import.

## Workflow — OpenSpec

This project is spec-driven. Before writing non-trivial code, check for an active change under `openspec/changes/` and work against its `tasks.md`.

- **Deep project context:** `openspec/config.yaml` (loaded by OpenSpec skills; read it before proposing).
- **Current change:** `openspec/changes/add-v1-mvp/` (proposal, design, tasks, specs).
- **Invoke OpenSpec skills** (`openspec-propose`, `openspec-explore`, `openspec-apply-change`, `openspec-archive-change`) for change lifecycle work — don't hand-edit spec artifacts ad hoc.
- **Scope discipline:** when uncertain whether something belongs in the current change, prefer adding a v2 item to the backlog over expanding scope.
- **Migrations:** whenever a task creates or modifies an Alembic migration file, immediately run `cd apps/api && uv run alembic upgrade head` against the local database before marking the task done, so the schema is ready for manual testing.

## UI / Frontend design

When making any UI change in `apps/web/`, read **[`apps/web/UI_GUIDELINES.md`](apps/web/UI_GUIDELINES.md)** first. It documents the established design system: `dish-*` color tokens, typography roles, icon library, component classes, layout conventions, and interaction patterns.

## Conventions

- **Conventional Commits** (`feat:`, `fix:`, `chore:`, etc.) — enforced locally via the husky `commit-msg` hook (`commitlint`).
- Prefer the simplest thing that satisfies the spec; defer cleverness.
- Backend: Ruff-clean, async throughout, type-hinted.
- Frontend: typed API client from generated OpenAPI types — don't hand-write request/response shapes.
- **Port cleanup:** after starting the backend locally for any reason (OpenAPI codegen, manual testing), always kill the process when done — `lsof -ti :8000 | xargs kill -9`. The user runs the dev servers from their own terminal.

## Verify before declaring done

Run `npm run verify` (or `make verify`) at the repo root before claiming work is complete. The script runs the full backpressure suite — ruff, basedpyright, pytest, alembic check, biome, nuxi typecheck, codegen drift, vitest, playwright smoke — and prints a banner per step. **Treat a non-zero exit as "not done"**: identify the failing step, fix the underlying cause, and re-run until it exits clean. Don't ship around a red verify.

For UI work, an interactive Playwright MCP server is registered in `.mcp.json` at the repo root — Claude Code can drive a real browser (navigate, click, screenshot) against the running dev server while iterating.

## Predecessor app

There is an older Strapi-based recipe app still live. It is **not** being migrated in place — a handful of recipes will be scraped as seed data once the new schema lands. Schema decisions are not constrained by the old shape.
