## MODIFIED Requirements

### Requirement: Session via HttpOnly cookie

The system SHALL maintain authenticated sessions through a single HttpOnly,
Secure cookie. The cookie SHALL be cryptographically signed by the backend
and SHALL carry no readable identity data accessible to client JavaScript.
In production, the cookie SHALL be issued with `SameSite=Lax` so that it is
treated as a first-party cookie by the browser; this is possible because
the browser only ever contacts the API through the same origin that serves
the frontend (the API is reverse-proxied through the frontend deployment).
In non-production environments where the frontend and API run on different
local origins, the cookie SHALL be issued with `SameSite=Lax` and `Secure=False`.

#### Scenario: Authenticated request includes session cookie
- **WHEN** a signed-in browser makes a request to the API through the
  frontend-served `/api/...` path
- **THEN** the request automatically includes the session cookie and the
  backend resolves it to the authenticated user before handling the request

#### Scenario: Tampered cookie is rejected
- **WHEN** a request arrives with a session cookie whose signature does not
  validate
- **THEN** the backend treats the request as anonymous and clears the invalid
  cookie on the response

#### Scenario: Cookie is first-party in privacy-strict browsers
- **WHEN** a user signs in using a browser that blocks third-party cookies
  (e.g. DuckDuckGo, Brave, Safari with strict tracking prevention)
- **THEN** the session cookie is accepted and persisted by the browser, and
  subsequent API requests carry it

### Requirement: Sign in with GitHub

The system SHALL allow a visitor to sign in with their GitHub account using
OAuth 2.0 authorization code flow. On successful authentication, a user
record SHALL be created or updated, and an HttpOnly Secure session cookie
SHALL be set on the response. The OAuth callback URL registered with GitHub
SHALL point at the frontend-served `/api/auth/github/callback` path, not at
the API origin directly, so that the redirect-with-Set-Cookie response is
returned from the same origin the browser uses for all other API calls.

#### Scenario: First-time GitHub sign-in
- **WHEN** a visitor without an account clicks "Sign in with GitHub" and
  successfully authorizes the app on GitHub
- **THEN** the system creates a new `users` row with `provider = "github"`
  and `provider_id = <github user id>`, populates `email`, `name`, and
  `avatar_url` from the GitHub profile, sets a session cookie, and redirects
  the browser to the home page

#### Scenario: Returning GitHub sign-in
- **WHEN** a visitor whose `(provider, provider_id)` already exists clicks
  "Sign in with GitHub" and successfully authorizes
- **THEN** the system updates `name` and `avatar_url` from the latest GitHub
  profile, sets a session cookie, and redirects to the page they came from
  (or home if none)

#### Scenario: User declines GitHub authorization
- **WHEN** a visitor cancels or denies the GitHub OAuth prompt
- **THEN** the system redirects to the home page without setting a session
  cookie and surfaces a non-blocking message indicating sign-in did not
  complete

#### Scenario: GitHub redirects through the frontend-served callback
- **WHEN** GitHub completes authorization and redirects the user
- **THEN** the redirect target is `https://<frontend-host>/api/auth/github/callback`,
  the frontend deployment proxies that request to the backend, the backend's
  Set-Cookie response is returned to the browser as a first-party cookie on
  `<frontend-host>`, and the browser is redirected onward to the application

### Requirement: Sign in with Google

The system SHALL allow a visitor to sign in with their Google account using
OAuth 2.0 authorization code flow. The same upsert-and-cookie behavior as
GitHub SHALL apply. The OAuth callback URL registered with Google SHALL
point at the frontend-served `/api/auth/google/callback` path.

#### Scenario: First-time Google sign-in
- **WHEN** a visitor without an account signs in with Google for the first
  time
- **THEN** the system creates a new `users` row with `provider = "google"`
  and `provider_id = <google sub claim>`, populates `email`, `name`, and
  `avatar_url` from the Google profile, sets a session cookie, and redirects
  to the home page

#### Scenario: Same email across providers creates two accounts
- **WHEN** a visitor signs in with Google using an email that already exists
  on a `provider = "github"` account
- **THEN** the system creates a separate `users` row keyed on
  `(provider, provider_id)` — accounts are not auto-merged in v1

#### Scenario: Google redirects through the frontend-served callback
- **WHEN** Google completes authorization and redirects the user
- **THEN** the redirect target is `https://<frontend-host>/api/auth/google/callback`,
  the frontend deployment proxies that request to the backend, and the resulting
  Set-Cookie is observed by the browser as a first-party cookie on `<frontend-host>`
