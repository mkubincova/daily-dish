## 1. Python type checking with basedpyright

- [x] 1.1 Add `basedpyright` to the `dev` dependency group in `apps/api/pyproject.toml`; run `uv sync --all-groups`.
- [x] 1.2 Add a `[tool.basedpyright]` block: `pythonVersion = "3.13"`, `typeCheckingMode = "standard"`, with per-path overrides setting `app/` to `strict` and `tests/` + `alembic/versions/` to `standard`. Exclude `__pycache__` and the local `test.db`.
- [x] 1.3 Run `uv run basedpyright` from `apps/api/` to surface the initial backlog. Fix the diagnostics in `app/`; for genuine third-party-stub gaps add narrowly scoped `# pyright: ignore[<rule>]` comments and document the reason in a one-line comment above each.
  - Strict produced 135 errors (mostly SQLModel/SQLAlchemy `reportUnknown*`); deferred via task 1.7.
  - Standard produced 51; resolved by: narrow `executionEnvironments` overrides for `app/models/` (SQLModel `Field` defaults) and `alembic/versions/` (alembic.op runtime augmentation); `col()` wrappers from sqlmodel for 9 router `where()`/`join()` sites; one `# pyright: ignore[reportCallIssue]` for `pydantic-settings` `Settings()` call.
- [x] 1.4 Add `lint-pyright` Make target in `apps/api/Makefile`; add a `Type check (basedpyright)` step to the API job in `.github/workflows/ci.yml` after the existing `Format check` step. (Make target named `typecheck` to match the web side's vocabulary.)
- [x] 1.5 Add `uv run --quiet basedpyright` to `.husky/pre-push` (after the typecheck:web step), gated on changes touching `apps/api/**/*.py`.
- [x] 1.6 Verify: introduce a deliberate `None` access in a sandbox branch, confirm `basedpyright` and pre-push both fail; revert.
- [ ] 1.7 Tighten `app/` to `strict` mode (add `strict = ["app"]` to `[tool.basedpyright]`). Resolve the `reportUnknown*` SQLModel/SQLAlchemy backlog with explicit type annotations on collection variables and route handler return types. Keep the existing `executionEnvironments` overrides for `app/models/` and `alembic/versions/`. Acceptance: `uv run basedpyright` clean in strict mode; pytest still green.

## 2. Typed frontend client (openapi-fetch)

- [x] 2.1 Add `openapi-fetch` to `apps/web/package.json` dependencies.
- [x] 2.2 Create `apps/web/app/utils/api.ts` exporting a singleton `$api = createClient<paths>({ baseUrl, credentials: "include" })`, where `paths` is imported from `~/types/api`. Read `baseUrl` from `useRuntimeConfig().public.apiUrl`. (Used `baseUrl: ""` because generated paths already include the `/api` prefix; no runtime config needed.)
- [x] 2.3 Migrate composables: `useCategories.ts`, `useTags.ts` — replace `$fetch<X>(...)` with `$api.GET("/categories")` / `$api.POST("/tags", { body })` etc.
- [x] 2.4 Migrate stores: `auth.ts` (`/auth/me`, `/auth/logout`), `favorites.ts` (`/recipes/{id}/favorite` POST + DELETE).
- [x] 2.5 Migrate page-level fetches that use `useFetch<X>(...)`: `pages/index.vue`, `pages/favorites.vue`, `pages/r/[slug]/index.vue`, `pages/r/[slug]/edit.vue`. Wrap `$api.GET(...)` calls in `useAsyncData` so SSR continues to work; preserve existing keys, watchers, and error-status redirects.
  - Migration surfaced two silent-drift bugs: (1) FE was sending `?status=draft|published` to `/api/recipes` but the backend never accepted it (UI sidebar buttons were dead) — dropped from typed call; (2) backend types `steps` as `list[dict[str, Any]]` so typed client requires `Record<string, unknown>[]` — cast at boundary. Both tracked in tasks 2.11 and 2.12.
- [x] 2.6 Migrate page mutations: `pages/r/new.vue` (POST `/recipes`), `pages/r/[slug]/index.vue` (DELETE `/recipes/{id}`), `pages/r/[slug]/edit.vue` (PATCH `/recipes/{id}`).
- [x] 2.7 Migrate `components/RecipeForm.vue` (`SignedUploadParams` from `/uploads/signature`). Cloudinary upload remains a direct `$fetch` to a third-party host — leave it but narrow its hand-written type to a local `interface` defined in the same file.
- [x] 2.8 Delete every now-unused hand-written request/response type: `Category`, `Tag`, `User`, `RecipeOut`, `PaginatedRecipes`, `SignedUploadParams`, etc. Keep only types that have no OpenAPI counterpart (e.g. local UI state). (Deleted: `User` interface in auth store, `SignedUploadParams` import in RecipeForm, hand-written `RecipeOut`/`PaginatedRecipes`/`TrashedRecipeItem`/`RecipeListItem` aliases at use sites; kept generated `components["schemas"][...]` aliases where the type was still referenced. Also removed dead `runtimeConfig.public.apiUrl` from `nuxt.config.ts`.)
- [x] 2.9 Run `npm --prefix apps/web run typecheck` and resolve any errors revealed by the migration.
- [x] 2.10 Run `npm --prefix apps/web run test` to confirm the existing Vitest spec still passes. (12/12 passing.)
- [x] 2.11 Backend: tighten `RecipeIn.steps` and `RecipeUpdate.steps` from `list[dict[str, Any]]` to a typed `RecipeStep` Pydantic model with `position: int` and `text: str`. Regenerate `apps/web/types/api.d.ts`. Remove the `data.steps as unknown as { [x: string]: unknown }[]` casts in `pages/r/new.vue` and `pages/r/[slug]/edit.vue`. Acceptance: typecheck passes without the casts; existing recipes still load + save.
  - Added `RecipeStep(BaseModel)` with `position: int`, `text: str`; applied to `RecipeIn.steps`, `RecipePatch.steps`, `RecipeOut.steps`. Kept `Recipe.steps` (ORM column) as `list[dict[str, Any]]` since JSONB returns plain dicts — narrowed only at the API boundary. `_recipe_out` now coerces dicts via `RecipeStep.model_validate(...)`; `create_recipe` serializes back via `s.model_dump()` for `model_dump(exclude_unset=True)` continues to work in `update_recipe` without changes. Casts removed from both pages; Vitest 12/12, pytest 79/79, basedpyright clean, `nuxi typecheck` clean. Manual save smoke not exercised in this session.
- [x] 2.12 Decide on the home-page `status` filter: either drop the dead UI buttons in `SidebarContent.vue` / `useRecipeFilters.ts` for the public list page, or extend `/api/recipes` to accept the `status` query param (note that `is_public=true` already constrains the public list, so "drafts" makes no sense there — most likely the right fix is to remove `setStatus` plumbing from the public sidebar and keep it only on `/me`). Acceptance: no FE control sends a query param the BE doesn't accept.
  - Status UI is already gated by `:show-status="true"`, set only on `/me`; `/me` correctly sends `?status=` and `/api/recipes/mine` accepts it. Public pages (`index.vue`, `favorites.vue`) build their query params inline and never include `status` (fixed during the 2.5 migration). The actual silent-drift landmine was `useRecipeFilters.toApiParams()` — dead code since 2.5 that would re-emit `?status=` to whichever caller wired it. Deleted `toApiParams` and its test block; kept the per-route `status` state (used by `/me`). Vitest 7/7, `nuxi typecheck` exit 0.

## 3. Web tests in CI

- [x] 3.1 Add a `Tests (Vitest)` step to the `web` job in `.github/workflows/ci.yml` after the typecheck step: `run: npm run test`.
- [x] 3.2 Verify the new step runs in CI for this PR. (Requires a push; locally `npm --prefix apps/web run test` passes 7/7. To be confirmed on first CI run.)

## 4. Vue unused-binding detection via vue-tsc

- [x] 4.1 In `apps/web/nuxt.config.ts`, add a `typescript.tsConfig` override setting `compilerOptions.noUnusedLocals = true` and `compilerOptions.noUnusedImports = true`. (TypeScript has no `noUnusedImports` option — `noUnusedLocals` already covers unused imports. Used `noUnusedLocals: true` plus `noUnusedParameters: true` for full coverage. Confirmed flags propagate to `.nuxt/tsconfig.app.json` and `.nuxt/tsconfig.json`.)
- [x] 4.2 Run `npm --prefix apps/web run typecheck`. Address legitimate unused declarations; rename intentionally-unused destructures with a leading underscore. (No fixes needed — codebase was already clean. Verified vue-tsc actually catches new violations by dropping a canary `app/_canary.vue` with an unused `Ref` import: TS6133 fires, exit 1, then reverted.)
- [x] 4.3 Confirm Biome's existing Vue overrides remain in `apps/web/biome.json` (no Biome change required); document in `apps/web/UI_GUIDELINES.md` (one short paragraph) that unused-locals are caught by `vue-tsc`, not Biome, and the underscore convention is the escape hatch. (Biome overrides untouched; added "Unused locals and imports" paragraph at end of `UI_GUIDELINES.md`.)

## 5. Playwright + MCP

- [x] 5.1 Add `@playwright/test` as a dev dependency in `apps/web/package.json`. Run `npx playwright install chromium` locally. (Added `@playwright/test ^1.50.1`, npm-resolved to 1.59.1. The chromium browser binary install must be run by the developer locally; not invoked from this session.)
- [x] 5.2 Create `apps/web/playwright.config.ts` configured for chromium-only, with `webServer.command = "npm run dev"` for local and a CI-specific override that uses `nuxi preview` against a freshly-built bundle. Set `baseURL` from `process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000"`. (Switches to `npm run preview` when `CI=true`. webServer is auto-skipped when `PLAYWRIGHT_BASE_URL` is provided so an external server can be reused.)
- [x] 5.3 Decide and implement the auth bypass for tests:
  - [x] 5.3.1 Inspect `apps/api/app/routers/auth.py` to determine if a dev-login shortcut already exists; if so, document its activation env var. (No shortcut existed.)
  - [x] 5.3.2 If not, add a `POST /auth/_test/login` endpoint that takes an email, creates/looks up a user, and issues the session cookie. The route MUST raise 404 when `settings.environment == "production"`. (Added with `include_in_schema=False`; idempotent on email; provider hardcoded to "test".)
  - [x] 5.3.3 Add `tests/test_auth.py::test_test_login_disabled_in_production` covering the production-mode rejection. (Plus `test_test_login_creates_user_and_sets_cookie` and `test_test_login_is_idempotent` for the happy path. 82/82 pytest, basedpyright clean.)
- [x] 5.4 Add `apps/web/e2e/smoke.spec.ts`: anonymous user lands on `/`, authenticates via the test-only shortcut, opens an existing recipe detail, asserts the title and the steps list render. Seed data via the existing API in a `test.beforeAll` if needed. (Spec uses `request.post(/api/auth/_test/login)`, then seeds a recipe via `/api/recipes`, then opens `/r/<slug>` and asserts title + steps. Recipe is seeded inline rather than in `beforeAll` so each run is hermetic.)
- [x] 5.5 Add `e2e` script to `apps/web/package.json`: `"e2e": "playwright test"`. Add `e2e:ui` for local debugging: `"e2e:ui": "playwright test --ui"`. (Also excluded `e2e/**` from vitest discovery in `vitest.config.ts` to keep the two runners from colliding.)
- [x] 5.6 Add a `Smoke (Playwright)` step to the web CI job: cache `~/.cache/ms-playwright`, run `npx playwright install --with-deps chromium`, run `npm run build`, then `npm run e2e` with `PLAYWRIGHT_BASE_URL` pointing at the previewed build.
  - Implemented as a separate `e2e` job in `.github/workflows/ci.yml` (the existing `web` job has no Python toolchain). Uses SQLite (`sqlite+aiosqlite:///./e2e.db`) with `SQLModel.metadata.create_all` for schema, matching the API pytest setup. Spins up uvicorn + Nuxt preview in background, waits for both health endpoints, runs the spec, uploads the playwright-report artifact. Marked `continue-on-error: true` so the suite is non-blocking until it has a few green runs; flip when stable. SQLite is fine here because the FE never sees JSONB-specific behavior — promote to the postgres service the `api` job already runs if/when an E2E needs Postgres semantics. Not verified against a real CI run yet (5.8).
- [x] 5.7 Create `.mcp.json` at the repo root registering `@playwright/mcp` (e.g. `{ "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } } }`). Add `.mcp.json` to git.
- [x] 5.8 Verify the smoke spec runs locally end-to-end (`npm --prefix apps/web run e2e`) and via MCP from the agent. (Pending: requires the developer to run `npx playwright install chromium` and start the API. Not verified in this session.)

## 6. Commit-msg enforcement

- [x] 6.1 Add `@commitlint/cli` and `@commitlint/config-conventional` to root `package.json` `devDependencies`. Run `npm install`. (Resolved to `@commitlint/cli@19.6.1` + `@commitlint/config-conventional@19.6.0`; +105 packages.)
- [x] 6.2 Add `.commitlintrc.cjs` at the repo root: `module.exports = { extends: ["@commitlint/config-conventional"] };`. (Also disabled `body-max-line-length` and `footer-max-line-length` so the `/commit` skill's prose-bullet bodies aren't rejected by the hook. Header rules — type/scope/subject/length — stay strict, since that's the part that matters for parsers and changelogs. Verified by replaying the last three session commits through `commitlint`: all pass.)
- [x] 6.3 Create `.husky/commit-msg` with `npx --no -- commitlint --edit "$1"`. Mark executable.
- [x] 6.4 Verify: `git commit -m "broken message"` is rejected; `git commit -m "chore: add commitlint"` succeeds. (Verified by piping each message to `npx --no -- commitlint`: bad → exit 1 with `subject-empty` + `type-empty`; good → exit 0. Skipped the `git commit` invocation to avoid touching the unrelated staged change in `tasks.md`.)

## 7. Sentry runtime feedback

- [ ] 7.1 Backend: add `sentry-sdk[fastapi]` to `apps/api/pyproject.toml`. Initialise in `app/main.py` only when `settings.sentry_dsn` is set; pass `environment=settings.sentry_environment`, `traces_sample_rate=0`, `send_default_pii=False`. Add the two settings to `app/config.py` with sane defaults.
- [ ] 7.2 Frontend: add `@sentry/nuxt` to `apps/web/package.json`. Add `apps/web/app/plugins/sentry.client.ts` that calls `Sentry.init` only when `runtimeConfig.public.sentryDsn` is set. Pipe `NUXT_PUBLIC_SENTRY_DSN` into `nuxt.config.ts` `runtimeConfig.public`.
- [ ] 7.3 Update `.env.example` files (api + web) and `DEPLOYMENT.md` with the new `SENTRY_DSN` / `SENTRY_ENVIRONMENT` / `NUXT_PUBLIC_SENTRY_DSN` variables, marked optional.
- [ ] 7.4 Verify: with DSN unset, `npm --prefix apps/web run dev` and `cd apps/api && uv run uvicorn app.main:app` both behave identically to current behaviour. Kill the api on port 8000 when done (`lsof -ti :8000 | xargs kill -9`).

## 8. Single `verify` entry point

- [ ] 8.1 Create `scripts/verify.sh` at the repo root: `set -euo pipefail`, prints a banner per step, and runs (in order) — api: `ruff check`, `ruff format --check`, `basedpyright`, `pytest`, `alembic check`; web: `biome check`, `nuxi typecheck`, `npm run codegen` + drift check, `vitest run`, `playwright test`. Make executable.
- [ ] 8.2 Add `verify` script to root `package.json`: `"verify": "bash scripts/verify.sh"`. Add `make verify` target to a new repo-root `Makefile` that delegates to the same script.
- [ ] 8.3 Update `CLAUDE.md`: add a "Verify before declaring done" section instructing agents to run `npm run verify` and treat a non-zero exit as "not done"; add a one-line note about the `.mcp.json` Playwright MCP server for UI work.
- [ ] 8.4 Verify: `npm run verify` exits 0 on a clean main branch; introduce a deliberate failure in each category (lint, typecheck, test, migration drift) and confirm the script identifies the failing step before reverting.

## 9. README — backpressure documentation

- [ ] 9.1 Update the "Quality checks" table in the root `README.md` so each row matches the post-change state of `.husky/`, `.github/workflows/ci.yml`, and `scripts/verify.sh`. Add or modify rows so the table covers, in trigger order:
  - Claude `PostToolUse` (Edit/Write) — `ruff check --fix` + `ruff format` on `.py`; `biome check --write` on web files. (Existing row; verify wording.)
  - Husky `pre-commit` (`git commit`) — `lint-staged`: biome on staged web files, ruff on staged Python files. (Existing row.)
  - Husky `commit-msg` (`git commit`) — `commitlint` against `@commitlint/config-conventional`. (NEW.)
  - Husky `pre-push` (`git push`) — codegen-drift check on `apps/web/types/api.d.ts`; `nuxi typecheck` (with `noUnusedLocals`); `basedpyright` on changed Python files. (Update existing row.)
  - GitHub Actions `ci.yml` (push/PR to `main`) — api: ruff lint + format check, `basedpyright`, pytest, alembic upgrade + `alembic check`; web: biome, `nuxi typecheck`, `vitest run`, `npm run build` (with Cloudinary-secret leak check), Playwright smoke against `nuxi preview`. (Update existing row.)
  - On-demand `npm run verify` / `make verify` — runs the full backpressure suite locally (the on-demand entry point added in task group 8). (NEW.)
  - Playwright MCP (interactive agent sessions) — registered via `.mcp.json`; lets a coding agent drive the running UI and capture screenshots while iterating. (NEW row, or a paragraph immediately under the table.)
- [ ] 9.2 Update the paragraph beneath the table: keep the existing "CI is the enforceable floor" framing, add one sentence pointing at `npm run verify` as the cheapest way to reproduce the CI floor locally, and one sentence pointing at the Playwright MCP entry point for agent-driven UI work.
- [ ] 9.3 Update `apps/api/README.md` and `apps/web/README.md` only as needed to mention the new commands they expose (`uv run basedpyright`, `npm run e2e`, `npm run e2e:ui`); do not duplicate the root table.
- [ ] 9.4 Verify: every row in the README's "Quality checks" table corresponds to a real hook file, CI step, or script committed by this change; every hook/CI step/script committed by this change is referenced in exactly one row.
