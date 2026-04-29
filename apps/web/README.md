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

The frontend uses a typed client generated from the backend's OpenAPI spec. The generated file is committed at `types/api.d.ts` and is what the build uses.

**Whenever the backend API schema changes, regenerate locally and commit the result:**

```bash
# Backend must be running on http://localhost:8000
npm run codegen
git add types/api.d.ts
```

Codegen is **not** part of `npm run build` — Vercel has no backend to fetch from. If you forget to regenerate after a backend change, the frontend will type-check against a stale schema.

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
- Vercel runs `npm run build`; codegen is **not** in the build, so make sure `types/api.d.ts` is up to date before pushing
