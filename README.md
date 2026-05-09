# Daily Dish

A personal recipe app and portfolio project. Browse public recipes without signing in; sign in with GitHub or Google to create, edit, and manage your own.

## Stack

| Layer     | Technology                                                        |
| --------- | ----------------------------------------------------------------- |
| Frontend  | Nuxt 3 (Vue 3, SSR), Pinia, Tailwind — deployed on Vercel         |
| Backend   | FastAPI (Python 3.12+), SQLModel, async — deployed on Railway     |
| Database  | PostgreSQL 16 (Railway) + Alembic migrations                      |
| Auth      | OAuth (GitHub + Google) → HttpOnly cookie sessions                |
| Images    | Cloudinary — browser uploads direct, backend-signed               |
| API types | FastAPI OpenAPI → `openapi-typescript` typed client at build time |

## Monorepo layout

```
daily-dish/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Nuxt 3 frontend
├── openspec/         # Specs and design docs
├── docker-compose.yml
└── README.md
```

## Quick start

```bash
# Install root tooling (husky hooks, lint-staged)
npm install

# Start local Postgres
docker compose up -d

# API
cd apps/api
cp .env.example .env   # fill in your values
make db-migrate
make dev               # http://localhost:8000

# Web
cd apps/web
cp .env.example .env
npm install
npm run dev            # http://localhost:3000
```

## Quality checks

Checks are layered so errors surface as close to the keystroke as possible. Later layers catch anything the earlier ones missed or that was bypassed.

| Layer                            | Trigger               | Runs                                                                                                                                                                                                                                                                                                      |
| -------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude `PostToolUse`             | After each Edit/Write | `ruff check --fix` + `ruff format` on `.py`; `biome check --write` on web files                                                                                                                                                                                                                           |
| Husky `pre-commit`               | `git commit`          | `lint-staged` → biome on staged web files, ruff on staged Python files (auto re-stage)                                                                                                                                                                                                                    |
| Husky `commit-msg`               | `git commit`          | `commitlint` against `@commitlint/config-conventional` (header rules strict; body/footer wrap relaxed)                                                                                                                                                                                                    |
| Husky `pre-push`                 | `git push`            | `apps/web/types/api.d.ts` codegen-drift check; `nuxi typecheck` (with `noUnusedLocals`); `basedpyright` on changed Python files                                                                                                                                                                           |
| GitHub Actions (`ci.yml`)        | push / PR to `main`   | **api job:** ruff lint + format, `basedpyright`, pytest (SQLite), `alembic upgrade` + `alembic check` (Postgres). **web job:** biome, `nuxi typecheck`, `vitest run`, `npm run build` (with Cloudinary-secret leak check). **e2e job:** uvicorn + `nuxi preview` + Playwright smoke (`continue-on-error`) |
| `npm run verify` / `make verify` | On-demand             | The full local backpressure suite — every check above, in one shell-out, with a banner per step                                                                                                                                                                                                           |

For UI work, an interactive Playwright MCP server is registered in `.mcp.json` at the repo root, so a Claude Code session can launch a real browser, navigate, and screenshot against the running dev server while iterating — no committed spec required.

Hook activation requires `npm install` at the repo root (Husky's `prepare` script registers `.husky/` as git's hooks path). The Claude `PostToolUse` hook lives in `.claude/hooks/post_edit.sh` and is only active in Claude Code sessions. CI is the enforceable floor — local hooks are skippable (`--no-verify`) and exist to shorten the feedback loop, not to replace the pipeline. `npm run verify` is the cheapest way to reproduce that floor locally before pushing.

## Design decisions

Architecture decisions (separated deploys, REST+OpenAPI, SQLModel, HttpOnly cookies, etc.) are documented in [`openspec/changes/archive/2026-04-24-add-v1-mvp/design.md`](openspec/changes/archive/2026-04-24-add-v1-mvp/design.md).

## Attribution

Favicon graphics: [1f958.svg](https://github.com/twitter/twemoji/blob/master/assets/svg/1f958.svg) by Twitter, Inc and other contributors — [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).
