## ADDED Requirements

### Requirement: Frontend reverse-proxies the API
The Nuxt frontend SHALL be configured to reverse-proxy all browser requests to `/api/**` to the backend origin, so that the browser only ever contacts the frontend host. The proxy configuration SHALL preserve the `/api` path prefix end-to-end (i.e. `<frontend>/api/foo` is forwarded to `<backend>/api/foo`), and the backend origin SHALL be sourced from a server-side environment variable so it can be repointed without a code change.

#### Scenario: Browser request to the API is served via the frontend host
- **WHEN** the browser makes a request to `https://<frontend-host>/api/recipes`
- **THEN** the response is produced by the FastAPI backend, returned via the frontend deployment, and the browser observes the response as same-origin

#### Scenario: Proxy target is environment-driven
- **WHEN** the frontend is deployed to a different backend (e.g. a preview Railway service)
- **THEN** updating the backend URL environment variable on the frontend deployment is sufficient to repoint the proxy with no code change

### Requirement: API routes are mounted under `/api`
The FastAPI application SHALL serve every public route under a `/api` prefix (e.g. `/api/auth/github/login`, `/api/recipes`) so that the frontend's path-preserving proxy reaches them and so that `request.url_for(...)` generates correct OAuth callback URLs.

#### Scenario: Routes resolve under the `/api` prefix
- **WHEN** any HTTP client requests a route at `<backend>/api/<path>`
- **THEN** the route handler executes and responds with the expected payload

#### Scenario: Routes do NOT resolve at the bare path
- **WHEN** any HTTP client requests a route at `<backend>/<path>` without the `/api` prefix
- **THEN** the response is HTTP 404

## MODIFIED Requirements

### Requirement: Vercel monorepo configuration
The repository SHALL configure the Vercel project to build and deploy only the Nuxt frontend from `apps/web` as the project root, and the Nuxt configuration at `apps/web/nuxt.config.ts` SHALL declare a `routeRules` proxy on `/api/**` that forwards to the backend origin.

#### Scenario: Vercel detects Nuxt framework from monorepo
- **WHEN** Vercel imports the GitHub repository
- **THEN** the project root setting points Vercel to `apps/web` and the Nuxt framework is auto-detected

#### Scenario: Browser API calls reach the backend through the Vercel deployment
- **WHEN** the deployed frontend is loaded in a browser and the application makes a request to `/api/auth/github/login`
- **THEN** the Vercel deployment proxies the request to the backend, forwards standard `X-Forwarded-*` headers, and returns the backend's response to the browser

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
