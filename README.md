# Daily Dish

A personal recipe app and portfolio project. Browse public recipes without signing in; sign in with GitHub or Google to create, edit, and manage your own.

**Live site:** coming soon  
**API docs:** coming soon

---

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

| Layer                    | Trigger                    | Runs                                                                                   |
| ------------------------ | -------------------------- | -------------------------------------------------------------------------------------- |
| Claude `PostToolUse`     | After each Edit/Write      | `ruff check --fix` + `ruff format` on `.py`; `biome check --write` on web files        |
| Husky `pre-commit`       | `git commit`               | `lint-staged` → biome on staged web files, ruff on staged Python files (auto re-stage) |
| Husky `pre-push`         | `git push`                 | `vue-tsc` typecheck on the frontend                                                    |
| GitHub Actions (`ci.yml`) | push / PR to `main`        | ruff lint+format, pytest, `alembic upgrade` + `alembic check` (Postgres), biome, typecheck |

Hook activation requires `npm install` at the repo root (Husky's `prepare` script registers `.husky/` as git's hooks path). The Claude `PostToolUse` hook lives in `.claude/hooks/post_edit.sh` and is only active in Claude Code sessions. CI is the enforceable floor — local hooks are skippable (`--no-verify`) and exist to shorten the feedback loop, not to replace the pipeline.

## Design decisions

Architecture decisions (separated deploys, REST+OpenAPI, SQLModel, HttpOnly cookies, etc.) are documented in [`openspec/changes/archive/2026-04-24-add-v1-mvp/design.md`](openspec/changes/archive/2026-04-24-add-v1-mvp/design.md).

## Attribution

Favicon graphics: [1f958.svg](https://github.com/twitter/twemoji/blob/master/assets/svg/1f958.svg) by Twitter, Inc and other contributors — [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).
