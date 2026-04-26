### Requirement: Railway build and start configuration
The repository SHALL include `apps/api/railway.toml` declaring the build command, start command (with Alembic migration prefixed), and the `$PORT` binding so Railway can deploy the FastAPI service without any manual portal configuration of commands.

#### Scenario: Railway deploys API without manual command configuration
- **WHEN** Railway pulls the `apps/api/` directory
- **THEN** it MUST use the commands declared in `railway.toml` with no additional portal input required

#### Scenario: Alembic migrations run before server starts
- **WHEN** the Railway service starts (including re-deploys)
- **THEN** `alembic upgrade head` SHALL run to completion before `uvicorn` binds to `$PORT`

### Requirement: Vercel monorepo configuration
The repository SHALL include a `vercel.json` at the repo root that sets `rootDirectory` to `apps/web` so Vercel builds and deploys only the Nuxt frontend from a monorepo checkout.

#### Scenario: Vercel detects Nuxt framework from monorepo
- **WHEN** Vercel imports the GitHub repository
- **THEN** the `rootDirectory` setting SHALL point Vercel to `apps/web` and the Nuxt framework SHALL be auto-detected

### Requirement: Complete `.env.example` files
Both `apps/api/.env.example` and `apps/web/.env.example` SHALL enumerate every environment variable consumed by the respective app, with comments explaining each variable and where to obtain its value.

#### Scenario: Developer can identify every required env var from example files
- **WHEN** a developer reads `apps/api/.env.example`
- **THEN** every key in `app/config.py` Settings MUST have a corresponding entry with a descriptive comment

#### Scenario: Web env example covers all runtimeConfig keys
- **WHEN** a developer reads `apps/web/.env.example`
- **THEN** every key used in `nuxt.config.ts` runtimeConfig MUST have a corresponding entry with a comment

### Requirement: Deployment runbook
The repository SHALL include a `DEPLOYMENT.md` at the repo root that provides a step-by-step guide for a first-time deploy, covering: Railway Postgres provisioning, Railway service setup and env vars, Vercel project setup and env vars, GitHub OAuth app creation (with exact redirect URIs), Google OAuth app creation (with exact redirect URIs), Cloudinary configuration, and a post-deploy smoke test checklist.

#### Scenario: Developer can complete first deploy by following DEPLOYMENT.md alone
- **WHEN** a developer follows DEPLOYMENT.md in order
- **THEN** they SHALL have a running production environment without needing to consult external documentation for standard steps

#### Scenario: OAuth redirect URIs are explicitly stated
- **WHEN** the developer reads the OAuth sections of DEPLOYMENT.md
- **THEN** the exact callback URL pattern (e.g., `https://<api-domain>/auth/github/callback`) SHALL be provided so they can enter it in the OAuth portal without guessing

#### Scenario: CORS and session cookie requirements are called out
- **WHEN** the developer reads the Railway env var section
- **THEN** DEPLOYMENT.md SHALL explicitly state that `ENVIRONMENT=production` must be set and explain the cross-origin session cookie implication
