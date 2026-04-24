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

## Design decisions

Architecture decisions (separated deploys, REST+OpenAPI, SQLModel, HttpOnly cookies, etc.) are documented in [`openspec/changes/archive/2026-04-24-add-v1-mvp/design.md`](openspec/changes/archive/2026-04-24-add-v1-mvp/design.md).
