## ADDED Requirements

### Requirement: Add recipe to favorites

The system SHALL allow an authenticated user to mark any non-deleted recipe as a favorite by calling `POST /recipes/{id}/favorite`. The operation SHALL be idempotent: if the recipe is already favorited by that user, the system SHALL return success without creating a duplicate row.

#### Scenario: User favorites a recipe for the first time

- **WHEN** an authenticated user sends `POST /recipes/{id}/favorite` for a recipe they have not yet favorited
- **THEN** the system creates a `user_favorites` row with the user's id and the recipe's id, and returns HTTP 200 with the updated recipe summary including `is_favorited: true`

#### Scenario: User favorites a recipe they already favorited

- **WHEN** an authenticated user sends `POST /recipes/{id}/favorite` for a recipe already in their favorites
- **THEN** the system returns HTTP 200 without creating a duplicate row

#### Scenario: Unauthenticated user attempts to favorite

- **WHEN** an unauthenticated request hits `POST /recipes/{id}/favorite`
- **THEN** the system responds with HTTP 401

#### Scenario: Favoriting a soft-deleted recipe

- **WHEN** an authenticated user sends `POST /recipes/{id}/favorite` for a recipe whose `deleted_at` is not null
- **THEN** the system responds with HTTP 404

### Requirement: Remove recipe from favorites

The system SHALL allow an authenticated user to remove a recipe from their favorites by calling `DELETE /recipes/{id}/favorite`. The operation SHALL be idempotent: if the recipe is not in the user's favorites, the system SHALL return success.

#### Scenario: User removes a favorited recipe

- **WHEN** an authenticated user sends `DELETE /recipes/{id}/favorite` for a recipe currently in their favorites
- **THEN** the system deletes the `user_favorites` row and returns HTTP 204

#### Scenario: User removes a recipe not in their favorites

- **WHEN** an authenticated user sends `DELETE /recipes/{id}/favorite` for a recipe not in their favorites
- **THEN** the system returns HTTP 204 without error

#### Scenario: Unauthenticated user attempts to unfavorite

- **WHEN** an unauthenticated request hits `DELETE /recipes/{id}/favorite`
- **THEN** the system responds with HTTP 401

### Requirement: List the user's favorites

The system SHALL provide an authenticated endpoint `GET /users/me/favorites` that returns a paginated list of recipes the requesting user has favorited, ordered by when they were favorited (`user_favorites.created_at` descending). Only non-deleted recipes SHALL appear. The endpoint SHALL accept the same `category_items` and `tags` filter parameters as the public recipe list, with identical OR-within / AND-across semantics.

#### Scenario: Authenticated user loads their favorites

- **WHEN** an authenticated user requests `GET /users/me/favorites` with no filters
- **THEN** the system returns their favorited, non-deleted recipes ordered by most-recently-favorited first, with each recipe including at minimum: id, slug, title, description, image_url, created_at, is_favorited (always true), attached category-item ids, and attached tag ids

#### Scenario: Favorites list filtered by category

- **WHEN** an authenticated user requests `GET /users/me/favorites?category_items=main`
- **THEN** the system returns only their favorited recipes that are attached to the `main` category item

#### Scenario: Favorites list filtered by tag

- **WHEN** an authenticated user requests `GET /users/me/favorites?tags={id}`
- **THEN** the system returns only their favorited recipes that carry that tag

#### Scenario: No favorites returns empty page

- **WHEN** an authenticated user with no favorites requests `GET /users/me/favorites`
- **THEN** the system returns HTTP 200 with an empty `items` array

#### Scenario: Unauthenticated user hits favorites endpoint

- **WHEN** an unauthenticated request hits `GET /users/me/favorites`
- **THEN** the system responds with HTTP 401

#### Scenario: Soft-deleted recipe excluded from favorites list

- **WHEN** a recipe that a user has favorited is soft-deleted
- **THEN** that recipe no longer appears in the user's favorites list
