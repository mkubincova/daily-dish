# Spec — auth

## ADDED Requirements

### Requirement: Sign in with GitHub

The system SHALL allow a visitor to sign in with their GitHub account using
OAuth 2.0 authorization code flow. On successful authentication, a user
record SHALL be created or updated, and an HttpOnly Secure session cookie
SHALL be set on the response.

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

### Requirement: Sign in with Google

The system SHALL allow a visitor to sign in with their Google account using
OAuth 2.0 authorization code flow. The same upsert-and-cookie behavior as
GitHub SHALL apply.

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

### Requirement: Session via HttpOnly cookie

The system SHALL maintain authenticated sessions through a single HttpOnly,
Secure cookie. The cookie SHALL be cryptographically signed by the backend
and SHALL carry no readable identity data accessible to client JavaScript.

#### Scenario: Authenticated request includes session cookie
- **WHEN** a signed-in browser makes a request to the API
- **THEN** the request automatically includes the session cookie and the
  backend resolves it to the authenticated user before handling the request

#### Scenario: Tampered cookie is rejected
- **WHEN** a request arrives with a session cookie whose signature does not
  validate
- **THEN** the backend treats the request as anonymous and clears the invalid
  cookie on the response

### Requirement: Current user identity

The system SHALL expose an authenticated endpoint (`GET /auth/me`) that
returns the requesting user's own profile, including `email`, `name`,
`avatar_url`, and provider. Anonymous requests SHALL receive HTTP 401.

#### Scenario: Authenticated user fetches their own profile
- **WHEN** an authenticated user calls `GET /auth/me`
- **THEN** the system returns their full profile including their email

#### Scenario: Anonymous user fetches profile
- **WHEN** an anonymous request calls `GET /auth/me`
- **THEN** the system responds with HTTP 401

### Requirement: Sign out

The system SHALL provide a sign-out action that invalidates the current
session.

#### Scenario: User signs out
- **WHEN** a signed-in user invokes sign-out
- **THEN** the backend clears the session cookie on the response, and
  subsequent requests are treated as anonymous

### Requirement: Public read access without authentication

The system SHALL allow anonymous (unauthenticated) requests to read public
recipes — both the public list and individual public recipe detail pages —
without redirecting to sign-in.

#### Scenario: Anonymous visitor browses recipes
- **WHEN** an unauthenticated visitor requests the public recipe list or any
  recipe whose `is_public` is true and `deleted_at` is null
- **THEN** the system returns the recipe data without prompting for sign-in

#### Scenario: Anonymous visitor requests a draft recipe
- **WHEN** an unauthenticated visitor requests a recipe whose `is_public` is
  false
- **THEN** the system responds with HTTP 404 (not 401, to avoid confirming
  the resource exists)

### Requirement: Owner-based authorization for write operations

The system SHALL restrict create, update, and soft-delete operations on a
recipe to the user identified as its owner. Authentication alone is not
sufficient — the authenticated user MUST match `recipes.user_id`.

#### Scenario: Owner edits their own recipe
- **WHEN** the authenticated user is the owner of the target recipe and
  submits an update
- **THEN** the system applies the update and returns the updated recipe

#### Scenario: Authenticated non-owner attempts to edit
- **WHEN** an authenticated user who is not the owner attempts to update or
  soft-delete a recipe
- **THEN** the system responds with HTTP 404 (not 403, to avoid confirming
  the resource exists to non-owners)

#### Scenario: Anonymous user attempts to create a recipe
- **WHEN** an unauthenticated request attempts to create a recipe
- **THEN** the system responds with HTTP 401
