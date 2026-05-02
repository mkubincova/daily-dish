## Context

Daily Dish currently runs as two separate deployments: Nuxt 3 frontend on Vercel (`*.vercel.app`) and FastAPI backend on Railway (`*.up.railway.app`). The frontend calls the backend directly using an absolute `NUXT_PUBLIC_API_URL`. Because the two hosts have different registrable domains, the auth cookie issued by the backend is a **third-party** cookie from the browser's perspective, set with `SameSite=None; Secure`.

DuckDuckGo's mobile browser (and other tracker-blocking browsers) silently drop third-party cookies regardless of per-site protection toggles, so OAuth login fails on those browsers — the user authenticates successfully, but the redirect lands on the frontend with no session cookie attached, and the next API call returns 401.

The cleanest fix is to make the cookie first-party. Two options achieve that: (a) buy a custom domain and host frontend and backend on subdomains of a shared parent, or (b) make the browser only ever talk to one origin by reverse-proxying the API through Vercel. This change pursues (b): no recurring cost, fully reversible, and (a) can layer on top later by simply pointing the custom domain at Vercel.

## Goals / Non-Goals

**Goals:**
- OAuth sign-in works in DuckDuckGo, Brave, Safari, and Firefox on mobile and desktop.
- Auth cookie is first-party (`SameSite=Lax; Secure`) in production.
- Browser never directly contacts the Railway origin in production.
- Zero additional recurring cost.
- Reversible: a future custom-domain migration is a small config change, not a re-architecture.

**Non-Goals:**
- Buying or configuring a custom domain (deferred — not blocked by this change).
- Merging frontend and backend into one deployment (architectural rule: separate FE+BE deploys remain).
- Changing OAuth provider or auth library.
- Re-implementing the frontend API client; only its base URL changes.
- Eliminating direct Railway access for ops/debugging — Railway URL still works for `curl` and OpenAPI introspection during development.

## Decisions

### Decision 1: Nuxt server route using h3 `proxyRequest`

Implement the proxy as a Nuxt server route at `apps/web/server/routes/api/[...path].ts` that calls h3's `proxyRequest` to forward `/api/**` to the Railway origin with the `/api` prefix preserved. The handler sets `fetchOptions: { redirect: "manual" }` and injects custom forwarding headers (see Decision 6).

**Why:** A `routeRules.proxy` declaration in `nuxt.config.ts` was the original plan, but two requirements made a server route the better fit:
1. **OAuth redirects must reach the browser, not be followed server-side.** The OAuth callback responds with a 302 to the frontend that carries `Set-Cookie`. Nitro's default proxy follows redirects server-side, which would cause the cookie to be set on the proxy-internal fetch and lost. `proxyRequest`'s `fetchOptions.redirect: "manual"` opts out of automatic redirect-following so the 302 is forwarded verbatim.
2. **Custom forwarding headers must be injected per request.** The standard `X-Forwarded-*` headers are mangled by Railway's edge (see Decision 6); we need to attach `x-original-host` / `x-original-proto` ourselves, which `routeRules.proxy` does not support.

Configuration of the backend origin still lives outside code — the handler reads `NUXT_API_PROXY_TARGET` at request time.

**Alternatives considered:**
- *`nuxt.config.ts` `routeRules` proxy* (the original proposal): rejected for the two reasons above.
- *Vercel `rewrites` in `vercel.json`*: rejected — the project removed `vercel.json` recently because it conflicted with monorepo root-directory detection (commit `3289130`), and a Nitro-level mechanism avoids that pitfall entirely.
- *A Vercel Edge Function*: rejected — extra surface area when a Nitro server route covers the same need.

### Decision 2: Preserve the `/api` path prefix end-to-end

Configure the proxy as `/api/**` → `https://<railway>/api/**` (prefix preserved) and mount FastAPI routers under a global `/api` prefix.

**Why:** Authlib's OAuth flow constructs the callback URL via FastAPI's `request.url_for("oauth_callback", ...)`, which derives its base from the incoming request URL plus `--proxy-headers`. If the proxy strips `/api`, FastAPI generates a callback URL without the prefix, OAuth providers redirect to a path Vercel doesn't proxy, and the user lands on a 404. Preserving the prefix lets `url_for()` produce correct, browser-reachable callback URLs without code-level URL manipulation.

A global router prefix (`include_router(..., prefix="/api")` or a single `APIRouter(prefix="/api")` parent) is the simplest mechanism. Direct Railway access continues to work — the API simply lives at `https://<railway>/api/...` instead of the root.

**Alternatives considered:**
- *Strip the prefix and set FastAPI's `root_path="/api"`*: rejected — `root_path` is intended for situations where the app is deployed behind a path prefix and is forwarded the prefix via `X-Forwarded-Prefix` (which Vercel does not send). It also makes the OpenAPI spec slightly trickier to consume directly via Railway.
- *Hard-code the callback URL via env var (`OAUTH_CALLBACK_BASE_URL`)*: rejected — duplicates information already implicit in the request, and creates a footgun where a forgotten env var produces wrong-but-syntactically-valid URLs.

### Decision 3: `SameSite=Lax` in production

Now that the cookie is set on the same origin the browser will use for subsequent requests, switch from `SameSite=None` to `SameSite=Lax` in production. `Secure=True` stays.

**Why:** `Lax` is the modern default for first-party session cookies; `None` is only required for legitimate cross-site contexts. Using `Lax` removes the cookie's "third-party-looking" signature that some privacy heuristics still flag.

**Alternatives considered:**
- *`SameSite=Strict`*: rejected — would break OAuth's top-level navigation flow (the post-callback redirect from `<railway>/api/auth/.../callback` to the frontend would not include the cookie if Strict were enforced before navigation completed). Lax allows top-level GETs to carry cookies, which is exactly what OAuth callbacks need.
- *Leave at `SameSite=None`*: rejected — defeats the purpose. Even though the cookie is now first-party, `None` keeps it eligible for cross-site contexts and some browsers' heuristics treat `None` cookies more aggressively.

### Decision 4: Relax CORS on the API

Drop the production Vercel origin from `allow_origins`. Keep the localhost origins for development.

**Why:** Browser-side CORS no longer applies — requests are same-origin from the browser to Vercel, and the Vercel→Railway hop is server-to-server, where CORS is not enforced. The only browsers that will hit Railway directly are during local development against the deployed API, which is rare and intentional.

**Alternatives considered:**
- *Leave CORS unchanged*: acceptable but misleading — implies cross-site browser access is supported when it isn't.
- *Lock CORS to an empty list*: rejected — keeps localhost dev usable.

### Decision 5: Frontend uses relative `/api` URLs in the browser

The browser-side API client uses relative paths (`/api/recipes`) so it adopts whatever origin is serving the page. The Nuxt server-side data fetching (SSR) calls the backend directly via the existing absolute `NUXT_PUBLIC_API_URL` (or a new server-only var) to avoid a self-loop through the same Vercel function.

**Why:** Relative URLs are the simplest way to inherit the page's origin and they keep the proxy behavior implicit and obvious in DevTools (every request is to `<vercel>/api/...`). Server-side rendering on Vercel calling its own `/api/**` route would introduce an extra hop and risk recursion under unusual circumstances; calling Railway directly during SSR is harmless because there's no browser cookie to lose.

**Alternatives considered:**
- *Use absolute URLs everywhere with `NUXT_PUBLIC_API_URL=https://<vercel>/api`*: works but creates an unnecessary same-origin string at runtime and obscures intent.
- *Use absolute URLs to Railway in the browser, with the cookie domain shared somehow*: not possible without a shared parent registrable domain, which is the whole reason for this change.

### Decision 6: Custom `x-original-host` / `x-original-proto` headers (not `X-Forwarded-*`)

The Nuxt proxy forwards the original frontend host and scheme to the API using bespoke headers — `x-original-host` and `x-original-proto` — and a small ASGI middleware on the API (`ForwardedHostMiddleware` in `apps/api/app/middleware.py`) rewrites the scope's `host` header and `scheme` from those headers before any handler runs. This is what makes `request.url_for("oauth_callback", ...)` build a callback URL against the Vercel origin instead of Railway's.

**Why:** The original plan was to rely on the standard `X-Forwarded-Host` / `X-Forwarded-Proto` set, which uvicorn's `--proxy-headers` mode honors. In production this turned out not to work: Railway's edge (Fastly) normalizes the standard `X-Forwarded-*` headers and rewrites `X-Forwarded-Host` to its own origin before the request reaches the container, so `url_for()` produced Railway-flavoured callback URLs that GitHub's OAuth app rejected as not-registered. A bespoke header pair passes through the CDN untouched. The middleware is intentionally tiny and runs as the outermost layer so every downstream handler — including Authlib's URL construction — sees the rewritten host.

**Alternatives considered:**
- *Standard `X-Forwarded-Host` + `--proxy-headers`*: rejected — Fastly rewrites it. (Tried first; commit `39c2ab9` added the middleware honoring `X-Forwarded-Host`, but commit `1081a1f` switched to the custom-header pair after observing the rewrite in production.)
- *Hard-code the callback base URL via env var*: rejected for the same reason as in Decision 2 — duplicates information already implicit in the request and creates a footgun.
- *Have the API trust a configured `FRONTEND_URL` for callback construction*: rejected — entangles the OAuth callback URL with a separate env var whose semantics are "where to redirect after successful login" and would make multi-environment deploys (preview URLs) brittle.

## Risks / Trade-offs

- **Latency overhead** → Every browser API call now hops through Vercel's edge before reaching Railway. Typical added latency is 50–150ms, negligible for a recipe-browsing app. *Mitigation:* none needed for v1; revisit if perceived sluggishness becomes a complaint.
- **Vercel function/bandwidth quotas** → Proxying every API call counts against the Vercel free tier's bandwidth and (depending on plan) function-invocation limits. *Mitigation:* personal-scale traffic is far below free-tier ceilings; monitor the Vercel usage dashboard once a month.
- **Existing sessions break at cutover** → Browsers holding a cookie issued under the old `SameSite=None` flag and the old origin will not see it on the new `/api/**` paths. *Mitigation:* acceptable — only the developer is logged in today; document a "sign in again after deploy" expectation in `DEPLOYMENT.md` and accept the one-time inconvenience.
- **Direct Railway access still issues third-party-style cookies** → If anyone hits the Railway URL directly (e.g. via a stale bookmark), they'll authenticate against a cookie that won't be sent on the Vercel-routed flow. *Mitigation:* low likelihood for a single-user app; long-term remediation is to gate Railway-direct access behind an allow-list or simply not advertise the Railway URL.
- **OpenAPI codegen target** → The frontend's `openapi-typescript` step runs against the Railway URL. After this change, that still works (Railway serves the spec at `/api/openapi.json`). *Mitigation:* update the codegen command's URL once and document it.
- **Local dev unchanged but slightly diverges from prod** → In dev, the frontend calls `http://localhost:8000` directly (no proxy hop). This is fine but means the dev environment doesn't exercise the proxy. *Mitigation:* a once-per-change manual smoke test on the deployed Vercel preview is sufficient for a personal project.

## Migration Plan

1. Land all code changes on a feature branch (Nuxt config, FastAPI router prefix, cookie flag, CORS, env example, runbook).
2. Deploy to a Vercel preview URL pointed at the existing Railway service.
3. In the GitHub OAuth App and Google OAuth Client, **add** (not replace) the new Vercel-routed callback URLs alongside the existing Railway ones.
4. Smoke-test sign-in on the preview URL using DuckDuckGo mobile, Chrome mobile, and Safari desktop.
5. Promote to the production Vercel domain.
6. Remove the old Railway-direct callback URLs from the OAuth configs once production is verified.

**Rollback:** revert the merge commit. The OAuth configs accept both old and new callback URLs during migration, so reverting the FE/API code reverts behavior cleanly. Old browser sessions remain invalid until the user signs in again — this is true for both forward and rollback.
