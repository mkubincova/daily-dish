# Daily Dish Web

Nuxt 3 frontend for the Daily Dish recipe app.

## Dev setup

**Prerequisites:** Node 22+

```bash
cd apps/web
cp .env.example .env
npm install
npm run dev          # http://localhost:3000
```

The app expects the FastAPI backend at `NUXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## Environment variables

| Variable | Description |
|---|---|
| `NUXT_PUBLIC_API_URL` | Backend API base URL (no trailing slash) |

Do **not** add any Cloudinary secrets here — those stay server-side in the API.

## OpenAPI codegen

The frontend uses a typed client generated from the backend's OpenAPI spec.

```bash
# Regenerate types (requires the API to be running)
npm run codegen
```

The generated file is committed to `types/api.d.ts` so CI can verify the client is up to date.

The `npm run build` command runs codegen first, and **CI fails if codegen fails** (i.e. if the backend is unreachable or the schema breaks).

## Linting

```bash
npm run lint         # check
npm run lint:fix     # fix
```

## Build

```bash
npm run build
```

## Deployment (Vercel)

- Set root directory to `apps/web` in Vercel project settings
- Set `NUXT_PUBLIC_API_URL` to your Railway backend URL
- Vercel automatically runs `npm run build` (which includes codegen)
