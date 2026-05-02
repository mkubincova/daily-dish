### Requirement: Railway build and start configuration
The repository SHALL include `apps/api/railway.toml` declaring the build command, start command (with Alembic migration prefixed), and the `$PORT` binding so Railway can deploy the FastAPI service without any manual portal configuration of commands.

#### Scenario: Railway deploys API without manual command configuration
- **WHEN** Railway pulls the `apps/api/` directory
- **THEN** it MUST use the commands declared in `railway.toml` with no additional portal input required

#### Scenario: Alembic migrations run before server starts
- **WHEN** the Railway service starts (including re-deploys)
- **THEN** `alembic upgrade head` SHALL run to completion before `uvicorn` binds to `$PORT`

### Requirement: Vercel monorepo configuration
The repository SHALL configure the Vercel project to build and deploy only the Nuxt frontend from `apps/web` as the project root, and `apps/web` SHALL include a Nitro server route at `server/routes/api/[...path].ts` that proxies all `/api/**` browser requests to the backend origin (sourced from `NUXT_API_PROXY_TARGET`) with the `/api` prefix preserved, redirects forwarded to the browser rather than followed server-side, and original-host / original-scheme metadata propagated to the backend through forwarding headers that survive the upstream CDN.

#### Scenario: Vercel detects Nuxt framework from monorepo
- **WHEN** Vercel imports the GitHub repository
- **THEN** the project root setting points Vercel to `apps/web` and the Nuxt framework is auto-detected

#### Scenario: Browser API calls reach the backend through the Vercel deployment
- **WHEN** the deployed frontend is loaded in a browser and the application makes a request to `/api/auth/github/login`
- **THEN** the Vercel deployment proxies the request to the backend, propagates the original frontend host and scheme via forwarding headers that the backend uses to construct OAuth callback URLs, and returns the backend's response (including any `Set-Cookie` and `Location` headers from a 302 redirect) verbatim to the browser without following the redirect server-side

### Requirement: Complete `.env.example` files
Both `apps/api/.env.example` and `apps/web/.env.example` SHALL enumerate every environment variable consumed by the respective app, with comments explaining each variable and where to obtain its value.

#### Scenario: Developer can identify every required env var from example files
- **WHEN** a developer reads `apps/api/.env.example`
- **THEN** every key in `app/config.py` Settings MUST have a corresponding entry with a descriptive comment

#### Scenario: Web env example covers all runtimeConfig keys
- **WHEN** a developer reads `apps/web/.env.example`
- **THEN** every key used in `nuxt.config.ts` runtimeConfig MUST have a corresponding entry with a comment

### Requirement: Deployment runbook
The repository SHALL include a `DEPLOYMENT.md` at the repo root that provides a step-by-step guide for a first-time deploy, covering: Railway Postgres provisioning, Railway service setup and env vars, Vercel project setup and env vars (including the backend-origin variable consumed by the frontend proxy), GitHub OAuth app creation (with exact redirect URIs), Google OAuth app creation (with exact redirect URIs), Cloudinary configuration, and a post-deploy smoke test checklist that includes a sign-in test in a privacy-focused browser (e.g. DuckDuckGo).

#### Scenario: Developer can complete first deploy by following DEPLOYMENT.md alone
- **WHEN** a developer follows DEPLOYMENT.md in order
- **THEN** they SHALL have a running production environment without needing to consult external documentation for standard steps

#### Scenario: OAuth redirect URIs are explicitly stated and use the frontend host
- **WHEN** the developer reads the OAuth sections of DEPLOYMENT.md
- **THEN** the exact callback URL pattern is provided as `https://<frontend-host>/api/auth/<provider>/callback`, reflecting that the browser-facing origin is the frontend deployment, not the backend

#### Scenario: Same-origin cookie behavior is explained
- **WHEN** the developer reads the Railway env var section
- **THEN** DEPLOYMENT.md SHALL explicitly state that `ENVIRONMENT=production` must be set, that the production session cookie is `SameSite=Lax; Secure` because the API is reverse-proxied through the frontend host, and that the frontend deployment must have its backend-origin env var set to the Railway URL

#### Scenario: Privacy-browser smoke test is part of the post-deploy checklist
- **WHEN** the developer reaches the post-deploy smoke test checklist
- **THEN** at least one item SHALL require signing in via a browser known to block third-party cookies (DuckDuckGo, Brave, or Safari with strict tracking prevention) to verify the first-party cookie behavior end-to-end

### Requirement: Frontend reverse-proxies the API
The Nuxt frontend SHALL be configured to reverse-proxy all browser requests to `/api/**` to the backend origin, so that the browser only ever contacts the frontend host. The proxy configuration SHALL preserve the `/api` path prefix end-to-end (i.e. `<frontend>/api/foo` is forwarded to `<backend>/api/foo`), and the backend origin SHALL be sourced from a server-side environment variable so it can be repointed without a code change.

#### Scenario: Browser request to the API is served via the frontend host
- **WHEN** the browser makes a request to `https://<frontend-host>/api/recipes`
- **THEN** the response is produced by the FastAPI backend, returned via the frontend deployment, and the browser observes the response as same-origin

#### Scenario: Proxy target is environment-driven
- **WHEN** the frontend is deployed to a different backend (e.g. a preview Railway service)
- **THEN** updating the backend URL environment variable on the frontend deployment is sufficient to repoint the proxy with no code change

### Requirement: API honors original-host forwarding headers
The FastAPI application SHALL apply an outermost ASGI middleware that rewrites the request's host and scheme from caller-supplied forwarding headers before any handler builds URLs from the request, so that URL construction (notably `request.url_for()` for OAuth callbacks) produces URLs against the original browser-facing origin rather than the upstream backend origin. The forwarding headers SHALL be a bespoke pair (not the standard `X-Forwarded-*` set), because the upstream CDN normalizes the standard headers.

#### Scenario: OAuth callback URL is built against the frontend host
- **WHEN** the proxy forwards a request to the backend with the original frontend host and scheme attached as forwarding headers
- **THEN** any URL built from the request inside the backend (in particular the OAuth `redirect_uri`) uses the frontend host and scheme, not the backend's own host

#### Scenario: Missing forwarding headers leave the request untouched
- **WHEN** a request reaches the backend without the forwarding headers (e.g. a direct curl against the backend)
- **THEN** the backend processes the request using its actual host and scheme without error

### Requirement: API routes are mounted under `/api`
The FastAPI application SHALL serve every application route (auth, recipes, categories, tags, favorites, uploads) under a `/api` prefix (e.g. `/api/auth/github/login`, `/api/recipes`) so that the frontend's path-preserving proxy reaches them and so that `request.url_for(...)` generates correct OAuth callback URLs. Infrastructure-only endpoints (the platform health probe at `/health`, plus the OpenAPI spec and docs at `/openapi.json` / `/docs` / `/redoc`) MAY remain at the bare root so platform health checks and direct schema introspection do not require the prefix.

#### Scenario: Application routes resolve under the `/api` prefix
- **WHEN** any HTTP client requests an application route at `<backend>/api/<path>`
- **THEN** the route handler executes and responds with the expected payload

#### Scenario: Application routes do NOT resolve at the bare path
- **WHEN** any HTTP client requests an application route (e.g. `<backend>/recipes`) without the `/api` prefix
- **THEN** the response is HTTP 404

#### Scenario: Health probe is reachable at the bare root
- **WHEN** the platform requests `<backend>/health`
- **THEN** the route handler executes and returns a 200 response indicating service health
