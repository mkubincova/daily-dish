## Why

OAuth sign-in does not work in privacy-focused mobile browsers (DuckDuckGo confirmed; Brave, Safari with strict ITP, and Firefox with strict ETP exhibit the same class of failure). The session cookie is set by the API on a different registrable domain (`*.up.railway.app`) than the frontend (`*.vercel.app`), so the browser treats it as a third-party cookie and discards it. Disabling DuckDuckGo's tracker protections per-site does not relax its cross-site cookie policy, so there is no in-browser workaround.

Buying a custom domain and sharing a parent (e.g. `app.example.com` + `api.example.com`) would also fix this, but the project has no budget for a domain right now and we want a reversible solution that keeps the door open for adding a custom domain later without re-architecting.

## What Changes

- Route all browser-to-API traffic through the Vercel deployment via a Nuxt `routeRules` proxy on `/api/**`, so the auth cookie is set on — and read from — the same origin the frontend lives on.
- **BREAKING** for browsers: switch the production session cookie from `SameSite=None` to `SameSite=Lax`. Existing sessions issued under the old cookie keep working until expiry but no new cross-site cookies are issued. (No DB or API contract break.)
- Mount FastAPI routers under a `/api` prefix so the Vercel proxy forwards path-preserved requests (e.g. `/api/auth/github/callback`) and FastAPI's `request.url_for()` generates correct callback URLs.
- Switch the frontend API client to call relative `/api/...` URLs instead of an absolute `NUXT_PUBLIC_API_URL`.
- Update GitHub and Google OAuth app callback URLs to the new Vercel-routed paths (`https://<vercel-domain>/api/auth/<provider>/callback`).
- Relax CORS on the API: with FE→API now same-origin from the browser's perspective, the only direct callers are the Vercel edge (server-to-server, CORS not enforced) and local dev. Production CORS allow-list can drop the Vercel origin.
- Update `DEPLOYMENT.md` to reflect the new architecture, the new OAuth callback pattern, the relaxed CORS expectations, and how to swap the proxy target later if a custom domain is added.

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `auth`: the session cookie requirement changes from cross-site (`SameSite=None; Secure`) to first-party via proxy (`SameSite=Lax; Secure`), and the OAuth callback URL pattern changes to a Vercel-routed path.
- `deployment-config`: the Vercel monorepo config gains a `routeRules` proxy declaration; the OAuth callback URI pattern documented in `DEPLOYMENT.md` changes; the cross-origin cookie callout in the Railway section is replaced with a same-origin-via-proxy explanation.

## Impact

- **Frontend** (`apps/web/`): `nuxt.config.ts` gains a `routeRules` proxy and the API client base URL becomes relative. `NUXT_PUBLIC_API_URL` becomes a server-only var consumed by the proxy target rather than the browser.
- **Backend** (`apps/api/`): all routers re-mounted under `/api` prefix; cookie `samesite` flag changes in `app/deps.py`; CORS allow-list trimmed in `app/main.py`. No DB migration required.
- **OAuth providers**: new callback URLs must be added to the GitHub OAuth App and Google OAuth Client. Old callbacks can be left in place during the cutover and removed afterward.
- **Performance**: every API request adds one Vercel edge → Railway hop (~50–150ms typical). Acceptable for a personal recipe app.
- **Cost**: $0. Stays within Vercel and Railway free tiers.
- **Reversibility**: the proxy is a config change in one file; reverting to direct API calls is a small diff if a custom domain is later adopted.
