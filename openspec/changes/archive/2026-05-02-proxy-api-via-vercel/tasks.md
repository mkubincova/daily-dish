## 1. Backend — mount routes under `/api`

- [x] 1.1 In `apps/api/app/main.py`, add a `/api` prefix to every `app.include_router(...)` call (auth, categories, tags, recipes, favorites, uploads) — or wrap them in a single parent `APIRouter(prefix="/api")` and include that.
- [x] 1.2 Verify any health-check or root route (`GET /`) is either also moved under `/api` or kept at the root intentionally; document the choice in a one-line comment if kept at root.
- [x] 1.3 Update `apps/api/tests/` so test client paths reflect the `/api` prefix; run `cd apps/api && uv run pytest` and confirm all tests pass.
- [x] 1.4 Start the API locally (`cd apps/api && uv run uvicorn app.main:app --port 8000 --proxy-headers`) and curl `http://localhost:8000/api/auth/me` and `http://localhost:8000/openapi.json` to confirm routing. Kill port 8000 after testing (`lsof -ti :8000 | xargs kill -9`).

## 2. Backend — first-party cookie + CORS

- [x] 2.1 In `apps/api/app/deps.py`, change `samesite="none" if is_prod else "lax"` to `samesite="lax"` in both `set_session_cookie` and `clear_session_cookie`.
- [x] 2.2 In `apps/api/app/main.py`, remove the production frontend origin from `CORSMiddleware.allow_origins`; keep only the localhost origins needed for dev. Add a one-line comment explaining that production is same-origin via the Vercel proxy.
- [x] 2.3 Re-run the API test suite.
- [x] 2.4 Add `apps/api/app/middleware.py` defining `ForwardedHostMiddleware`, an ASGI middleware that rewrites the scope's `host` header from `x-original-host` and `scheme` from `x-original-proto` so `request.url_for()` builds OAuth callback URLs against the Vercel origin. Register it as the outermost middleware in `apps/api/app/main.py` so it runs before any handler that constructs URLs. Cover it with a test in `tests/test_auth.py` that asserts the rewrite happens.
  - *Note:* not in the original plan. Standard `X-Forwarded-Host` + uvicorn `--proxy-headers` was tried first (commit `39c2ab9`) but Railway's Fastly edge rewrites the standard header to its own origin, so the proxy and middleware switched to the bespoke `x-original-host` / `x-original-proto` pair (commit `1081a1f`).

## 3. Frontend — proxy and relative URLs

- [x] 3.1 Add a Nuxt server route at `apps/web/server/routes/api/[...path].ts` that uses h3's `proxyRequest` to forward to `${NUXT_API_PROXY_TARGET}${event.path}` (preserving the `/api` prefix). Pass `fetchOptions: { redirect: "manual" }` so OAuth 302s are returned to the browser instead of followed server-side, and inject `x-original-host` / `x-original-proto` headers built from `getRequestHost(event, { xForwardedHost: true })` and `getRequestProtocol(...)`. Default the target to `http://localhost:8000` for local dev.
  - *Note:* the original plan called for a `routeRules` entry in `nuxt.config.ts`, but `routeRules.proxy` cannot disable redirect-following or inject custom headers; a server route is required for both.
- [x] 3.2 Update `runtimeConfig.public.apiUrl` to default to `/api` (relative). Keep an absolute fallback (`process.env.NUXT_PUBLIC_API_URL`) only for SSR/server contexts that legitimately call the backend directly during render; if no SSR data fetching uses it, remove the absolute fallback and consume `/api` everywhere.
- [x] 3.3 Audit the API client (`apps/web/...`) for any place that hard-codes the absolute API URL or assumes a non-`/api` path. Update to use the relative `/api/...` form.
- [x] 3.4 Update the OpenAPI codegen command (script in `package.json` or wherever `openapi-typescript` is invoked) to fetch the spec from `${NUXT_API_PROXY_TARGET}/openapi.json` (the spec is served at the root, not under `/api`). Also drop codegen from the Vercel build script — it requires a running backend on `localhost:8000` that doesn't exist on Vercel; `types/api.d.ts` is the build's source of truth and is regenerated locally when the API schema changes (commit `c3759a5`).
- [x] 3.5 Run `npm run dev` in `apps/web/` and run the API in another terminal. Confirm a browser request to a local page issues network calls to `http://localhost:3000/api/...` and the responses are correct. Sign in via GitHub locally end-to-end.

## 4. Env vars and config files

- [x] 4.1 Add `NUXT_API_PROXY_TARGET` to `apps/web/.env.example` with a comment explaining it points to the backend origin (no trailing slash, no `/api` suffix — the proxy adds the prefix).
- [x] 4.2 Document the production value of `NUXT_API_PROXY_TARGET` (the Railway URL) in `DEPLOYMENT.md` under the Vercel env vars section.
- [x] 4.3 In `apps/api/.env.example`, update the `FRONTEND_URL` comment to note that this is now the only browser-visible origin (used for OAuth final-redirect targets and CORS in dev).

## 5. OAuth provider configuration (manual)

- [x] 5.1 In the GitHub OAuth App, add `https://<vercel-host>/api/auth/github/callback` to the Authorization callback URL list (alongside the existing Railway callback during cutover).
- [x] 5.2 In the Google OAuth Client, add `https://<vercel-host>/api/auth/google/callback` to the Authorized redirect URIs (alongside the existing Railway callback during cutover).
- [x] 5.3 Note the cutover plan in `DEPLOYMENT.md`: keep both callbacks during migration, remove the Railway-direct ones once production is verified.

## 6. Documentation

- [x] 6.1 Update `DEPLOYMENT.md`:
  - Replace the cross-origin cookie callout with a same-origin-via-proxy explanation.
  - Update OAuth callback URL examples to use `https://<frontend-host>/api/auth/<provider>/callback`.
  - Add `NUXT_API_PROXY_TARGET` to the Vercel env vars list.
  - Add a post-deploy smoke-test item: "sign in on a privacy-strict browser (DuckDuckGo / Brave / Safari with strict ITP)".
- [x] 6.2 Update `CLAUDE.md` Auth bullet to reflect the new SameSite=Lax cookie and same-origin-via-Vercel-proxy architecture.

## 7. Deploy and verify

- [x] 7.1 Push the branch, let Vercel build a preview deployment.
- [x] 7.2 On the preview URL, open DevTools → Network and confirm every API call goes to `<preview-host>/api/...`. Confirm `Set-Cookie` for `auth_token` shows `SameSite=Lax`, `Secure`, `HttpOnly`, and Domain matching the frontend host.
- [x] 7.3 Sign in on DuckDuckGo mobile against the preview URL and confirm the session persists (refreshing the page keeps the user signed in; a protected route loads).
- [x] 7.4 Sign in on Chrome mobile and Safari desktop against the preview URL and confirm parity.
  - *Note:* initial sign-in failed in production with a `redirect_uri_mismatch` from GitHub because Railway's Fastly edge rewrote `X-Forwarded-Host` to its own origin; resolved by commits `39c2ab9` (added `ForwardedHostMiddleware`) and `1081a1f` (switched to bespoke `x-original-host` / `x-original-proto` headers).
- [x] 7.5 Promote to production. Repeat 7.2–7.4 against the production URL.
- [x] 7.6 Remove the old Railway-direct OAuth callback URLs from GitHub and Google.
