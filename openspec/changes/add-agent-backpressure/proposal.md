## Why

Daily Dish has the *parts* of a good agent-feedback loop (Ruff, Biome, vue-tsc, Pytest, Vitest, alembic check, husky hooks, generated OpenAPI types) but several are wired up so that they fail silently — most notably, the generated `apps/web/types/api.d.ts` is regenerated on every push but never imported by application code, the web Vitest suite is never executed in CI, and Python has no static type checker. An agent (or future me) can change a Pydantic response shape, a Vue prop, or a SQLModel relationship and all the green lights stay green. This change closes those silent-drift gaps so the existing tooling actually pushes back on bad changes — i.e. provides "backpressure" — before they ship.

## What Changes

- Adopt `openapi-fetch` as the single typed HTTP client for the web app and migrate every `$fetch<HandWrittenType>(...)` / `useFetch<HandWrittenType>(...)` call site (composables, stores, pages, components) to consume the generated `types/api.d.ts`. Removes the largest source of silent FE/BE drift.
- Add `basedpyright` to the API as a dev dependency, configured for strict mode on `app/` and standard mode on `tests/`, and run it in pre-push and CI.
- Run `npm run test` (Vitest) in the web CI job — currently absent.
- Add Playwright to `apps/web/` with one smoke spec covering the cooking-mode golden path (login → list → recipe detail). Add an `.mcp.json` exposing the Playwright MCP server so an interactive agent can drive the browser and take screenshots while implementing UI changes.
- Add a `commit-msg` husky hook running `commitlint` against `@commitlint/config-conventional`, enforcing the Conventional Commits convention CLAUDE.md already mandates.
- Add a single "verify" entry point at the repo root (`npm run verify` and a `make verify` mirror) that runs the full backpressure suite — backend lint, format, type-check, tests, alembic check; frontend lint, type-check, codegen-drift, tests — and reference it from CLAUDE.md as the command an agent must run before declaring work done.
- Replace Biome's currently-disabled Vue unused-var/import rules with a `vue-tsc --noUnusedLocals` pass folded into the existing typecheck step (no second linter; cheapest option).
- Update the root `README.md` "Quality checks" table so a reader can tell at a glance which backpressure mechanism runs at which trigger (Claude PostToolUse → pre-commit → commit-msg → pre-push → CI → on-demand `verify`), and what each one catches. Mention the Playwright MCP entry point.

## Capabilities

### New Capabilities

- `agent-backpressure`: the suite of automated feedback mechanisms (typed API client wiring, Python type-checking, web test execution, Playwright + MCP, commit-msg enforcement, unified verify entry point) that ensure code-quality regressions surface as a failing local command or CI step rather than a silent green build.

### Modified Capabilities

_(none — no spec-level behavior of existing capabilities changes; this is dev-loop infrastructure on top of `auth`, `recipes`, etc.)_

## Impact

- **`apps/web/`**:
  - New dependency: `openapi-fetch`. New dev dependencies: `@playwright/test`, `@commitlint/cli`, `@commitlint/config-conventional`.
  - Migrated call sites: every file currently calling `$fetch<X>(...)` or `useFetch<X>(...)` in `composables/`, `stores/`, `pages/`, `components/`. Hand-written response/request types deleted.
  - New: `playwright.config.ts`, `e2e/` directory with smoke spec, `.mcp.json` at repo root.
- **`apps/api/`**:
  - New dev dependency: `basedpyright`.
  - New `[tool.basedpyright]` block in `pyproject.toml`.
- **Repo root**:
  - New: `.commitlintrc.cjs`, root `package.json` gains a `verify` script and `commitlint` devDeps, new `.husky/commit-msg` hook, `Makefile` (or `scripts/verify.sh`) at root.
  - `.lintstagedrc.mjs` unchanged (still runs Biome/Ruff on staged files only).
- **CI** (`.github/workflows/ci.yml`):
  - Web job gains `npm run test`, `npx playwright install --with-deps`, and a Playwright smoke step.
  - API job gains a `basedpyright` step.
- **CLAUDE.md**:
  - New "Verify before declaring done" section pointing at `npm run verify`.
  - Note about `.mcp.json` and Playwright MCP for UI verification.
- **`README.md`**:
  - "Quality checks" table updated with the new layers (basedpyright, vitest in CI, Playwright + MCP, commit-msg, on-demand `verify`).
- **No API contract changes. No DB migrations.** The migration to `openapi-fetch` is a pure refactor against types already generated from the unchanged OpenAPI document.
