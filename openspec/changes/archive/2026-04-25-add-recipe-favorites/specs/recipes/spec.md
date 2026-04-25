## MODIFIED Requirements

### Requirement: View recipe detail

The system SHALL serve recipe detail pages identified by slug. A recipe
SHALL be retrievable by anyone if `is_public` is true and `deleted_at` is
null. A recipe with `is_public` false SHALL be retrievable only by its
owner. Recipe detail responses SHALL include the attached category items
(as a list of `{ id, category_id }`) and the attached tags (as a list of
`{ id, name }`). When the requesting user is authenticated, the response SHALL
also include `is_favorited: bool` indicating whether the recipe is in the
requesting user's favorites. When the requesting user is not authenticated,
`is_favorited` SHALL be `null` or omitted.

#### Scenario: Anonymous user views a public recipe

- **WHEN** an anonymous request hits a recipe slug whose recipe is public
  and not deleted
- **THEN** the system returns the recipe with its ingredients (ordered by
  position), its steps (ordered by position within the JSONB array), its
  attached category items, and its attached tags; `is_favorited` is null or omitted

#### Scenario: Authenticated user views a recipe they have favorited

- **WHEN** an authenticated user requests a recipe that is in their favorites
- **THEN** the response includes `is_favorited: true`

#### Scenario: Authenticated user views a recipe they have not favorited

- **WHEN** an authenticated user requests a recipe not in their favorites
- **THEN** the response includes `is_favorited: false`

#### Scenario: Owner views their own draft recipe

- **WHEN** the owner requests a recipe whose `is_public` is false
- **THEN** the system returns the recipe normally, including its category
  items, tags, and `is_favorited`

#### Scenario: Anyone (including non-owner) requests a draft

- **WHEN** an anonymous user, or an authenticated user who is not the owner,
  requests a recipe whose `is_public` is false
- **THEN** the system responds with HTTP 404

### Requirement: List public recipes (chronological)

The system SHALL provide a paginated list endpoint that returns all recipes
where `is_public` is true and `deleted_at` is null, ordered by `created_at`
descending. The endpoint SHALL be accessible without authentication. When the
requesting user is authenticated, each recipe in the list SHALL include
`is_favorited: bool`. When the requesting user is not authenticated,
`is_favorited` SHALL be `null` or omitted.

#### Scenario: Anonymous visitor loads the home feed

- **WHEN** an anonymous request hits the public list endpoint
- **THEN** the system returns recipes ordered newest first, including for
  each recipe at minimum: id, slug, title, description, image_url, owner
  display name, created_at, attached category-item ids, attached tag ids;
  `is_favorited` is null or omitted

#### Scenario: Authenticated user loads the public recipe list

- **WHEN** an authenticated user requests the public recipe list
- **THEN** each recipe in the response includes `is_favorited: bool` reflecting
  whether that recipe is in the user's favorites

#### Scenario: Pagination with cursor

- **WHEN** the request includes a cursor or offset parameter
- **THEN** the system returns the next page of results in the same order

### Requirement: List the owner's own recipes (including drafts)

The system SHALL provide a list endpoint, available only to authenticated
users, that returns every recipe owned by the requesting user where
`deleted_at` is null, including those with `is_public` false. Order SHALL
be `created_at` descending. Each recipe in the response SHALL include
`is_favorited: bool`.

#### Scenario: Owner loads their /me recipe list

- **WHEN** an authenticated user requests their own recipe list
- **THEN** the system returns all their recipes, public and draft alike, in
  reverse-chronological order, including for each recipe its attached
  category-item ids, attached tag ids, and `is_favorited: bool`
