# Spec — recipes

## Requirements

### Requirement: Create recipe

The system SHALL allow an authenticated user to create a recipe owned by them.
A new recipe SHALL include a title, a slug derived from the title with a
short random suffix, optional description, optional servings, optional prep
and cook times, an `is_public` flag (default true), zero or more structured
ingredients, zero or more ordered steps stored as a JSONB array, zero or
more category-item associations referenced by `category_item_ids`, and zero
or more tag associations referenced by `tag_ids`. Tag references SHALL
identify pre-existing tags only — recipe creation SHALL NOT create new tags.

#### Scenario: Authenticated user creates a recipe

- **WHEN** an authenticated user submits a valid recipe payload
- **THEN** the system persists a new recipe with `user_id` set to the
  authenticated user, generates a unique slug, sets `created_at` and
  `updated_at`, persists the supplied category-item and tag associations,
  and returns the created recipe

#### Scenario: Slug uniqueness collision

- **WHEN** two recipes are created with titles that slugify to the same base
- **THEN** the random suffix on each slug ensures the final slugs differ, and
  both recipes are persisted successfully

#### Scenario: Validation failure on missing title

- **WHEN** a creation request omits the title or sends an empty title
- **THEN** the system responds with HTTP 422 and a validation error
  describing the missing field

#### Scenario: Unknown category item rejected

- **WHEN** a creation request includes a `category_item_ids` value that does
  not exist in the taxonomy
- **THEN** the system responds with HTTP 422

#### Scenario: Unknown tag rejected

- **WHEN** a creation request includes a `tag_ids` value that does not
  identify an existing tag
- **THEN** the system responds with HTTP 422

### Requirement: Update recipe

The system SHALL allow the owner of a recipe to update any of its fields,
including title (slug remains stable), description, servings, prep and cook
times, image URL and Cloudinary public id, source URL, ingredients, steps,
`is_public` flag, attached category items (`category_item_ids`), and
attached tags (`tag_ids`). Tag references SHALL identify pre-existing tags
only — recipe update SHALL NOT create new tags.

#### Scenario: Owner replaces ingredients and steps

- **WHEN** the owner submits an update containing a new full ingredients
  array and a new full steps array
- **THEN** the system replaces the previous ingredients (deleting old rows
  and inserting new ones) and replaces the JSONB steps in a single
  transaction, then returns the updated recipe

#### Scenario: Owner replaces category and tag associations

- **WHEN** the owner submits an update containing new full
  `category_item_ids` and `tag_ids` arrays
- **THEN** the system replaces the previous associations atomically with
  the supplied sets and returns the updated recipe

#### Scenario: Owner toggles visibility from public to draft

- **WHEN** the owner sets `is_public` to false on a previously public recipe
- **THEN** the recipe immediately disappears from the public list and detail
  page (anonymous requests return 404), but remains visible in the owner's
  own recipe list

### Requirement: Soft-delete recipe

The system SHALL allow the owner of a recipe to soft-delete it by setting
`deleted_at` to the current timestamp. Soft-deleted recipes SHALL be
excluded from all listings and detail responses, including the owner's own.
Soft-deleted recipes SHALL NOT be hard-deleted by v1 application code.

#### Scenario: Owner soft-deletes a recipe
- **WHEN** the owner issues a delete request for their recipe
- **THEN** the system sets `deleted_at`, returns HTTP 204, and subsequent
  requests for the recipe (by anyone, including the owner) return HTTP 404

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

### Requirement: Structured ingredients

The system SHALL store recipe ingredients as rows in a dedicated
`ingredients` table with the following structure: `recipe_id` (foreign key
to recipes), `position` (integer for ordering), `quantity` (numeric,
nullable), `unit` (text, nullable), `name` (text, required), and `notes`
(text, nullable).

#### Scenario: Ingredient with quantity and unit
- **WHEN** an ingredient is stored with quantity 1.5, unit "cups", name
  "all-purpose flour"
- **THEN** the system persists those values in their respective columns and
  returns them on read in the same shape

#### Scenario: Free-form ingredient without quantity
- **WHEN** an ingredient is stored with only a name (e.g. "salt to taste")
  and no quantity or unit
- **THEN** the system persists the row with quantity and unit as null

#### Scenario: Ingredients returned in order
- **WHEN** a recipe with multiple ingredients is read
- **THEN** the ingredients SHALL be returned ordered by `position` ascending

### Requirement: Steps stored as JSONB array

The system SHALL store recipe steps as a JSONB array on the `recipes`
table. Each step SHALL be an object with at minimum a `position` integer
and a `text` string. Updates SHALL replace the entire array atomically.

#### Scenario: Steps preserved in order
- **WHEN** a recipe is created with steps in a given order
- **THEN** the system persists them in that order and returns them in the
  same order on subsequent reads

#### Scenario: Editing replaces the full step list
- **WHEN** the owner submits an update containing a new steps array
- **THEN** the system replaces the previous steps with the new array
  atomically; partial-step updates are not supported

### Requirement: Image upload via Cloudinary signed parameters

The system SHALL provide an authenticated endpoint that returns Cloudinary
signed upload parameters (timestamp, signature, upload preset, and any
required public params). The Cloudinary API secret SHALL never leave the
backend. The frontend SHALL hold the selected file in local state and only
upload to Cloudinary at form-submit time, not on file pick. After the browser
uploads directly to Cloudinary, the frontend SHALL pass the resulting
`secure_url` and `public_id` back to the backend when creating or updating
the recipe, where they are stored as `image_url` and `image_public_id`.

When a PATCH request changes `image_public_id` to a different non-null value,
the backend SHALL destroy the previous Cloudinary asset (via the Destroy API)
after the DB write succeeds. If Destroy fails, the error SHALL be logged and
the response SHALL still succeed — a leaked asset is preferred over a failed
save.

#### Scenario: Authenticated user requests upload signature

- **WHEN** an authenticated user requests upload signing parameters
- **THEN** the system generates a fresh signature server-side using the
  Cloudinary API secret and returns the signed parameters to the client

#### Scenario: Unauthenticated user requests upload signature

- **WHEN** an unauthenticated request hits the upload-sign endpoint
- **THEN** the system responds with HTTP 401

#### Scenario: Recipe update persists Cloudinary image data

- **WHEN** the owner updates a recipe with `image_url` and
  `image_public_id` from a successful Cloudinary upload
- **THEN** the system stores both fields on the recipe and returns them on
  subsequent reads

#### Scenario: Image upload does not occur on file pick

- **WHEN** the user selects an image file in the recipe form
- **THEN** the file is held in local component state and no Cloudinary upload
  is initiated until the user submits the form

#### Scenario: Previous image is destroyed when replaced on update

- **WHEN** the owner submits a PATCH with a new `image_public_id` that differs
  from the current value
- **THEN** the system saves the new image fields, then calls Cloudinary Destroy
  for the old `image_public_id`

#### Scenario: Cloudinary Destroy fails on image replacement

- **WHEN** the PATCH succeeds but the Cloudinary Destroy call for the old
  image errors
- **THEN** the system logs the error with the old `image_public_id` and
  returns the updated recipe normally (HTTP 200)

### Requirement: Owner identity in public responses

The system SHALL identify a recipe's owner in publicly visible API responses
(recipe list, recipe detail) using only the owner's `name` (display name)
and `avatar_url`. The owner's `email` SHALL NOT appear in any response
returned to a user other than the owner themselves.

#### Scenario: Anonymous viewer reads a public recipe
- **WHEN** an anonymous request retrieves a public recipe
- **THEN** the response includes `owner.name` and `owner.avatar_url` but
  does not include `owner.email`

#### Scenario: Authenticated non-owner reads someone else's public recipe
- **WHEN** a signed-in user retrieves a public recipe owned by a different
  user
- **THEN** the response includes the other user's `name` and `avatar_url`
  but does not include their `email`

#### Scenario: Owner reads their own recipe
- **WHEN** the owner retrieves a recipe they own
- **THEN** the response includes the owner identity in the same shape
  (`name`, `avatar_url`); the owner can fetch their own email via
  `GET /auth/me`, not from the recipe payload

### Requirement: Source URL field reserved for future import

The system SHALL include a `source_url` text column (nullable) on recipes
from the initial schema. Owners MAY populate this field manually in v1 to
record where a recipe came from. Future URL-import features will populate
this field automatically without requiring a schema change.

#### Scenario: Owner manually sets source URL on create
- **WHEN** the owner creates a recipe with a `source_url` value
- **THEN** the system persists and returns that URL on the recipe

#### Scenario: Recipe with no source URL

- **WHEN** the owner creates or updates a recipe without setting
  `source_url`
- **THEN** the system stores `source_url` as null and the field is omitted
  or null in responses

### Requirement: Filter recipe lists by category items and tags

Both the public list endpoint and the owner-only list endpoint SHALL accept
optional filter parameters: `category_items` (one or more category-item
ids) and `tags` (one or more tag ids). Filter semantics SHALL be **OR
within a parameter, AND across parameters**: a recipe matches when it has
at least one of the requested category items per group AND at least one of
the requested tags. When the same parameter is repeated with different
values, each repetition is an independent AND-grouped clause.

#### Scenario: Single-category-item filter on public list

- **WHEN** an anonymous request hits `GET /recipes?category_items=soup`
- **THEN** the system returns only public, non-deleted recipes attached to
  the `soup` category item

#### Scenario: OR within a parameter

- **WHEN** a request hits `GET /recipes?category_items=soup,salad`
- **THEN** the system returns recipes attached to `soup` OR `salad` (or
  both)

#### Scenario: AND across different parameter groups

- **WHEN** a request hits
  `GET /recipes?category_items=soup,salad&category_items=vegetarian&tags=<christmas-id>`
- **THEN** the system returns only recipes that are (`soup` OR `salad`)
  AND `vegetarian` AND tagged `christmas`

#### Scenario: Filters apply identically to the owner list

- **WHEN** an authenticated user hits
  `GET /me/recipes?category_items=main&tags=<weeknight-id>`
- **THEN** the system applies the same filter semantics to the owner's own
  recipes (including drafts) and returns the matching subset

#### Scenario: No matches returns an empty page

- **WHEN** filter parameters narrow the result set to zero recipes
- **THEN** the system returns HTTP 200 with an empty `items` array and no
  next-page cursor

#### Scenario: Pagination cursor is invalidated when filters change

- **WHEN** a client supplies a cursor obtained under one filter set with a
  different filter set on the next request
- **THEN** the system returns the first page under the new filters and
  ignores the supplied cursor

#### Scenario: Unknown filter values yield no matches

- **WHEN** a request supplies a `category_items` or `tags` value that does
  not exist
- **THEN** the system returns HTTP 200 with an empty result set rather than
  an error

### Requirement: Filter the owner list by publication status

The owner-only list endpoint SHALL accept an optional `status` parameter
with values `published`, `draft`, or `all` (default). `published` SHALL
restrict results to recipes with `is_public = true`; `draft` SHALL
restrict to `is_public = false`; `all` SHALL apply no status filter. The
`status` filter SHALL combine with category and tag filters under the
same AND-across-parameters semantics.

#### Scenario: Owner filters to published recipes only

- **WHEN** an authenticated user hits `GET /me/recipes?status=published`
- **THEN** the system returns only recipes owned by the user where
  `is_public = true` and `deleted_at` is null

#### Scenario: Owner filters to drafts only

- **WHEN** an authenticated user hits `GET /me/recipes?status=draft`
- **THEN** the system returns only recipes owned by the user where
  `is_public = false` and `deleted_at` is null

#### Scenario: Status combines with category filter

- **WHEN** an authenticated user hits
  `GET /me/recipes?status=draft&category_items=main`
- **THEN** the system returns only the user's drafts that are also
  attached to the `main` category item

#### Scenario: Anonymous user supplying status is irrelevant

- **WHEN** an anonymous request hits the public list endpoint with a
  `status` parameter
- **THEN** the system ignores the parameter; the public list is always
  effectively `status=published`
