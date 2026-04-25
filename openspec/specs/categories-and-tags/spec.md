# Spec — categories and tags

## Requirements

### Requirement: Curated category taxonomy

The system SHALL maintain a curated taxonomy consisting of categories
and category items. A category SHALL have a stable text identifier
(e.g. `dish_type`). A category item SHALL have a stable text identifier
(e.g. `soup`) and SHALL belong to exactly one category. Identifiers
SHALL be lowercase ASCII with underscores. The taxonomy SHALL be
managed exclusively via Alembic migrations in this version; no
write endpoints SHALL be exposed.

#### Scenario: Initial taxonomy is seeded by migration

- **WHEN** the database migration introducing this capability runs
- **THEN** the system creates the categories `dish_type`, `mood`, and
  `protein` and their initial items in a single transaction

#### Scenario: Category item belongs to exactly one category

- **WHEN** an attempt is made to insert a `category_items` row whose
  `category_id` does not exist in `categories`
- **THEN** the database rejects the insert via foreign key constraint

### Requirement: Read categories and items

The system SHALL expose `GET /categories`, accessible without
authentication. The response SHALL list each category with its items
nested. The response payload SHALL include only stable identifiers —
no display labels, sort positions, icons, colors, or translations.

#### Scenario: Anonymous client requests categories

- **WHEN** an unauthenticated request hits `GET /categories`
- **THEN** the system returns HTTP 200 with a list of categories,
  each containing its `id` and an `items` array where each entry has
  an `id`

#### Scenario: Display metadata is not in the payload

- **WHEN** a client inspects the `GET /categories` response
- **THEN** no field named `label`, `position`, `icon`, `color`, or
  any locale-specific name appears on categories or items

### Requirement: Freeform tags created by authenticated users

The system SHALL allow any authenticated user to create a tag via
`POST /tags`. Tag names SHALL be normalised before persistence by
lowercasing, trimming surrounding whitespace, and collapsing runs of
internal whitespace to a single space. Tag names SHALL be unique after
normalisation.

#### Scenario: Authenticated user creates a new tag

- **WHEN** an authenticated user POSTs `{ "name": "Spicy" }` to `/tags`
- **THEN** the system stores a tag with `name = "spicy"`, sets
  `created_by` to the requesting user, sets `created_at`, and returns
  HTTP 201 with the tag

#### Scenario: Whitespace and casing variants normalise to the same tag

- **WHEN** a request POSTs `{ "name": "  Spicy   Dish " }` to `/tags`
- **THEN** the normalised name is `"spicy dish"` and the tag is stored
  with that name

#### Scenario: Posting an existing tag name returns the existing tag

- **WHEN** an authenticated user POSTs a tag name that, after
  normalisation, matches an existing tag
- **THEN** the system returns HTTP 200 with the existing tag without
  inserting a duplicate

#### Scenario: Anonymous user attempts to create a tag

- **WHEN** an unauthenticated request hits `POST /tags`
- **THEN** the system responds with HTTP 401

#### Scenario: Empty tag name is rejected

- **WHEN** a request POSTs a name that is empty after normalisation
  (empty string, whitespace only)
- **THEN** the system responds with HTTP 422 and a validation error

### Requirement: Read all tags

The system SHALL expose `GET /tags`, accessible without authentication,
returning all tags ordered alphabetically by `name`.

#### Scenario: Anonymous client requests the tag list

- **WHEN** an unauthenticated request hits `GET /tags`
- **THEN** the system returns HTTP 200 with all tags, each containing
  `id` and `name`, ordered alphabetically by `name`

### Requirement: Attach categories and tags to recipes

The system SHALL store the relationship between a recipe and its
category items in `recipe_category_items` (composite PK of
`recipe_id, category_item_id`), and between a recipe and its tags in
`recipe_tags` (composite PK of `recipe_id, tag_id`). Both relations
SHALL cascade-delete when the parent recipe is hard-deleted; soft
deletion of recipes SHALL NOT remove these association rows.

#### Scenario: Recipe is soft-deleted

- **WHEN** a recipe is soft-deleted by setting `deleted_at`
- **THEN** rows in `recipe_category_items` and `recipe_tags` for that
  recipe remain unchanged

#### Scenario: Same category item attached twice to a recipe

- **WHEN** an attempt is made to insert a duplicate
  `(recipe_id, category_item_id)` pair
- **THEN** the database rejects the insert via primary key constraint
