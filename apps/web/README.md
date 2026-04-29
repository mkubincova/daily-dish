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

The browser always talks to a same-origin `/api/**` path. A Nitro server route at `server/routes/api/[...path].ts` forwards those requests to the FastAPI backend, so cookies stay first-party. The backend origin is configured via `NUXT_API_PROXY_TARGET` (default `http://localhost:8000`).

## Environment variables

| Variable | Description |
|---|---|
| `NUXT_API_PROXY_TARGET` | Backend origin the Nitro proxy forwards to (e.g. `http://localhost:8000` locally, Railway URL in prod). No trailing slash, no `/api` suffix. |
| `NUXT_PUBLIC_GITHUB_CLIENT_ID` | GitHub OAuth client ID (public). |
| `NUXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID (public). |

Do **not** set `NUXT_PUBLIC_API_URL` — Nuxt would auto-map it onto `runtimeConfig.public.apiUrl` and override the `/api` default, sending the browser to the backend directly and breaking same-origin cookies.

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
- Set `NUXT_API_PROXY_TARGET` to the Railway backend URL (e.g. `https://daily-dish-production.up.railway.app`) — no trailing slash, no `/api` suffix
- Make sure `NUXT_PUBLIC_API_URL` is **not** set in Vercel (it would override the same-origin `/api` default and bypass the proxy, breaking auth cookies)
- Set `NUXT_PUBLIC_GITHUB_CLIENT_ID` and `NUXT_PUBLIC_GOOGLE_CLIENT_ID` to the production OAuth client IDs
- Vercel runs `npm run build`; codegen is **not** in the build, so make sure `types/api.d.ts` is up to date before pushing
