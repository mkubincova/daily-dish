# Spec — recipe-trash

## Requirements

### Requirement: List trashed recipes

The system SHALL provide an authenticated endpoint that returns all recipes owned by the requesting user where `deleted_at` is not null, ordered by `deleted_at` descending.

#### Scenario: Owner lists their trashed recipes

- **WHEN** an authenticated user requests `GET /me/recipes/trashed`
- **THEN** the system returns all their soft-deleted recipes (where `deleted_at` is not null) in reverse-chronological order of deletion, including at minimum: id, slug, title, image_url, deleted_at

#### Scenario: Unauthenticated request to trash list

- **WHEN** an unauthenticated request hits the trashed recipes endpoint
- **THEN** the system responds with HTTP 401

#### Scenario: Owner with no trashed recipes

- **WHEN** an authenticated user requests their trash and none of their recipes have been soft-deleted
- **THEN** the system returns HTTP 200 with an empty `items` array

### Requirement: Restore a soft-deleted recipe

The system SHALL allow the owner of a soft-deleted recipe to restore it by unsetting `deleted_at`. The restored recipe SHALL immediately reappear in the owner's active recipe list and, if `is_public` is true, in the public list.

#### Scenario: Owner restores a trashed recipe

- **WHEN** the owner sends `POST /recipes/{id}/restore` for a soft-deleted recipe they own
- **THEN** the system sets `deleted_at` to null, returns HTTP 200 with the restored recipe, and subsequent requests for that recipe return the full recipe as normal

#### Scenario: Restore a non-deleted recipe

- **WHEN** the owner sends `POST /recipes/{id}/restore` for a recipe that is not soft-deleted
- **THEN** the system responds with HTTP 409

#### Scenario: Non-owner attempts restore

- **WHEN** an authenticated user sends `POST /recipes/{id}/restore` for a recipe they do not own
- **THEN** the system responds with HTTP 403

### Requirement: Permanently delete a recipe and its image

The system SHALL allow the owner of a soft-deleted recipe to permanently delete it. Permanent deletion SHALL hard-delete the recipe row from the database and, if `image_public_id` is set, destroy the asset from Cloudinary via the Destroy API. This action is irreversible.

#### Scenario: Owner permanently deletes a trashed recipe with an image

- **WHEN** the owner sends `DELETE /recipes/{id}/permanent` for a soft-deleted recipe with a non-null `image_public_id`
- **THEN** the system hard-deletes the recipe row, calls Cloudinary Destroy for the `image_public_id`, and returns HTTP 204

#### Scenario: Owner permanently deletes a trashed recipe without an image

- **WHEN** the owner sends `DELETE /recipes/{id}/permanent` for a soft-deleted recipe with no image
- **THEN** the system hard-deletes the recipe row and returns HTTP 204 without calling Cloudinary

#### Scenario: Cloudinary Destroy fails during permanent delete

- **WHEN** the owner permanently deletes a recipe and the Cloudinary Destroy call fails
- **THEN** the system still hard-deletes the recipe row, logs the Cloudinary error (including the `image_public_id`), and returns HTTP 204

#### Scenario: Attempt to permanently delete a non-deleted recipe

- **WHEN** the owner sends `DELETE /recipes/{id}/permanent` for a recipe that has not been soft-deleted (i.e. `deleted_at` is null)
- **THEN** the system responds with HTTP 409

#### Scenario: Non-owner attempts permanent delete

- **WHEN** an authenticated user sends `DELETE /recipes/{id}/permanent` for a recipe they do not own
- **THEN** the system responds with HTTP 403

### Requirement: Trash view in the frontend

The system SHALL provide a `/me/trash` page visible only to authenticated users that lists the user's soft-deleted recipes. Each entry SHALL display the recipe title, deletion date, and actions for Recover and Delete Permanently. A Recover action SHALL restore the recipe. A Delete Permanently action SHALL prompt the user for confirmation before calling the permanent-delete endpoint.

#### Scenario: Owner visits trash page with trashed recipes

- **WHEN** an authenticated user navigates to `/me/trash`
- **THEN** the page lists their soft-deleted recipes with Recover and Delete Permanently actions

#### Scenario: Owner recovers a recipe from trash

- **WHEN** the owner clicks Recover on a trashed recipe
- **THEN** the recipe is removed from the trash list and the owner's active recipe list is updated

#### Scenario: Owner permanently deletes from trash

- **WHEN** the owner clicks Delete Permanently and confirms
- **THEN** the recipe is removed from the trash list and cannot be recovered

#### Scenario: Unauthenticated user visits trash page

- **WHEN** an unauthenticated user navigates to `/me/trash`
- **THEN** the page redirects to the login page

#### Scenario: Trash is empty

- **WHEN** an authenticated user visits `/me/trash` and has no trashed recipes
- **THEN** the page displays an empty state message
