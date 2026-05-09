## ADDED Requirements

### Requirement: Frontend HTTP calls SHALL be typed against the generated OpenAPI client

All frontend HTTP calls to the Daily Dish API MUST go through a typed client whose request and response shapes are derived from the OpenAPI document the backend publishes. Hand-written generic parameters on `$fetch<X>(...)` or `useFetch<X>(...)` are forbidden for routes the API exposes. Untyped fetches are limited to third-party endpoints (e.g. Cloudinary direct upload) and MUST still pass through `$fetch`'s built-in typing or an explicit narrow type.

#### Scenario: Backend response shape changes are caught at compile time

- **WHEN** a developer changes a Pydantic response model in `apps/api/app/`
- **AND** runs the codegen step (`npm run codegen` or pre-push)
- **THEN** the regenerated `apps/web/types/api.d.ts` reflects the new shape
- **AND** any frontend call site that assumed the old shape produces a TypeScript error during `nuxi typecheck`

#### Scenario: Adding a new request body field is type-checked

- **WHEN** a developer adds a required field to a `RecipeIn` payload model on the backend
- **AND** the frontend creates a recipe via the typed client without that field
- **THEN** `nuxi typecheck` fails locally and in CI

#### Scenario: Untyped third-party fetch remains allowed

- **WHEN** the frontend uploads to Cloudinary using a signed POST
- **THEN** that call MAY use `$fetch` directly with a hand-written type because Cloudinary is not part of the Daily Dish OpenAPI document

### Requirement: Python type errors SHALL fail pre-push and CI

The API SHALL be type-checked by `basedpyright` in `app/` (strict mode) and `tests/` (standard mode). Pre-push and the CI `api` job MUST run the type checker and fail on any diagnostic error.

#### Scenario: Latent None access is caught

- **WHEN** an agent writes `recipe.author.name` where `author` is `User | None`
- **AND** runs `npm run verify` or `git push`
- **THEN** the type checker reports the unsafe access and the command exits non-zero

#### Scenario: CI rejects type regressions

- **WHEN** a PR introduces a `basedpyright` error
- **THEN** the GitHub Actions `api` job fails before the deploy step

### Requirement: The web Vitest suite SHALL run in CI

The `web` CI job MUST execute `npm run test` (Vitest) and fail on any test failure. Pre-existing and new Vitest specs MUST be included in this run.

#### Scenario: Failing unit test blocks merge

- **WHEN** a PR breaks `apps/web/tests/useRecipeFilters.test.ts`
- **THEN** the CI `web` job fails

### Requirement: A Playwright smoke test SHALL guard the UI golden path

The repository MUST include a Playwright project under `apps/web/` with at least one smoke spec covering the cooking-mode golden path: anonymous landing page → authenticated session → recipe list → recipe detail. The smoke spec MUST run against `nuxi preview` (or equivalent production-mode build) in CI and fail the build on any assertion error.

#### Scenario: Recipe detail page render regression is caught

- **WHEN** a change accidentally removes the recipe-title element from `pages/r/[slug]/index.vue`
- **THEN** the Playwright smoke spec fails locally (`npm run e2e`) and in CI

#### Scenario: Auth bypass for tests is environment-gated

- **WHEN** the smoke spec authenticates via the test-only login shortcut
- **THEN** that shortcut MUST be available only when `ENV != "production"`
- **AND** an automated test in `apps/api/tests/test_auth.py` MUST verify the shortcut is rejected when `ENV == "production"`

### Requirement: An interactive agent SHALL be able to drive the browser via MCP

The repository MUST include an `.mcp.json` at the root that registers a Playwright MCP server, so an interactive coding agent can navigate, interact with, and screenshot the running UI without bespoke per-task wiring.

#### Scenario: Agent verifies a UI change end-to-end

- **WHEN** an agent edits a Vue component
- **AND** has access to the configured MCP servers
- **THEN** the agent can open the page in a real browser, capture a screenshot, and use the result to confirm the change before declaring the task done

### Requirement: Commit messages SHALL follow Conventional Commits

A `commit-msg` git hook MUST run `commitlint` against `@commitlint/config-conventional`. Non-conforming messages MUST be rejected before a commit is recorded.

#### Scenario: Free-form commit message is rejected

- **WHEN** a developer attempts `git commit -m "made some fixes"`
- **THEN** the commit-msg hook exits non-zero
- **AND** no commit is recorded

#### Scenario: Conventional message is accepted

- **WHEN** a developer attempts `git commit -m "fix(web): ensure recipe slug encoding"`
- **THEN** the commit succeeds

### Requirement: A single `verify` command SHALL run the full backpressure suite

The repository MUST expose a single command — `npm run verify` at the repo root, mirrored by `make verify` — that executes the entire backpressure suite: backend lint, format check, type check, tests, and migration drift; frontend lint, type check (with unused-locals enabled), codegen drift, unit tests, and Playwright smoke. The command MUST fail-fast and surface which step failed.

#### Scenario: Single command surfaces a failing step

- **WHEN** a developer runs `npm run verify` with a known type error in `apps/api/app/routers/recipes.py`
- **THEN** the command exits non-zero
- **AND** the printed output identifies `basedpyright` as the failing step

#### Scenario: CLAUDE.md instructs agents to run verify before declaring done

- **WHEN** a coding agent reads `CLAUDE.md`
- **THEN** it finds an explicit instruction to run `npm run verify` and treat a non-zero exit as "not done"

### Requirement: Vue unused-binding regressions SHALL be caught by the typecheck step

The frontend typecheck MUST be configured so that unused local variables and unused imports — including those inside `<script setup>` blocks of `*.vue` files — produce diagnostic errors via `vue-tsc`. The typecheck step MUST run in pre-push and CI.

#### Scenario: Unused script-setup binding fails typecheck

- **WHEN** a `*.vue` file declares `const unused = ref(0)` and never references it
- **THEN** `nuxi typecheck` reports an unused-locals error and exits non-zero

#### Scenario: Underscore-prefixed binding is permitted

- **WHEN** a `*.vue` file declares `const _unused = ref(0)` to deliberately mark intent
- **THEN** the typecheck step does NOT flag the binding

### Requirement: The README SHALL document where each backpressure mechanism runs

The root `README.md` MUST contain a "Quality checks" table that lists every backpressure layer present in the repository (Claude PostToolUse hook, husky `pre-commit`, husky `commit-msg`, husky `pre-push`, GitHub Actions CI, on-demand `verify`, Playwright MCP), the trigger that activates each layer, and the concrete tools each one runs. The table MUST stay in sync with `.husky/`, `.github/workflows/ci.yml`, and `scripts/verify.sh`.

#### Scenario: Reader can identify the typecheck layer

- **WHEN** a reader opens the root `README.md`
- **THEN** the "Quality checks" table indicates that `nuxi typecheck` runs at husky `pre-push` and in CI, and that `basedpyright` runs at husky `pre-push` and in CI

#### Scenario: Reader can identify the on-demand verify entry point

- **WHEN** a reader opens the root `README.md`
- **THEN** the table includes a row for `npm run verify` (and `make verify`) describing it as the on-demand command that runs the full backpressure suite locally

#### Scenario: Reader can identify the agent's UI-verification path

- **WHEN** a reader opens the root `README.md`
- **THEN** the table or its accompanying paragraph mentions the `.mcp.json`-registered Playwright MCP server as the way an interactive coding agent drives the UI

