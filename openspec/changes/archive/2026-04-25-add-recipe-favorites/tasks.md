## 1. Database

- [x] 1.1 Create `UserFavorite` SQLModel with `id` (UUIDv7), `user_id`, `recipe_id`, `created_at`; add unique constraint on `(user_id, recipe_id)`
- [x] 1.2 Generate Alembic migration for the `user_favorites` table

## 2. Backend — Schemas

- [x] 2.1 Add `is_favorited: bool | None` to the recipe response schema (null for unauthenticated callers)
- [x] 2.2 Create request/response schemas for the favorites endpoints (if needed beyond the recipe schema)

## 3. Backend — Endpoints

- [x] 3.1 Implement `POST /recipes/{id}/favorite` — idempotent, returns 200 with `is_favorited: true`
- [x] 3.2 Implement `DELETE /recipes/{id}/favorite` — idempotent, returns 204
- [x] 3.3 Implement `GET /users/me/favorites` — paginated, supports `category_items` and `tags` filters, ordered by `user_favorites.created_at` desc

## 4. Backend — Enrich existing endpoints with `is_favorited`

- [x] 4.1 Update `GET /recipes` to LEFT JOIN `user_favorites` and include `is_favorited` when the caller is authenticated
- [x] 4.2 Update `GET /recipes/{slug}` to include `is_favorited` for authenticated callers
- [x] 4.3 Update `GET /users/me/recipes` to include `is_favorited` for the authenticated owner

## 5. Backend — Tests

- [x] 5.1 Test `POST /recipes/{id}/favorite`: first favorite, duplicate, unauthenticated, deleted recipe
- [x] 5.2 Test `DELETE /recipes/{id}/favorite`: remove existing, remove non-existent, unauthenticated
- [x] 5.3 Test `GET /users/me/favorites`: empty list, with favorites, with category/tag filters, unauthenticated
- [x] 5.4 Test `is_favorited` in recipe list and detail responses for authenticated vs anonymous callers

## 6. Frontend — OpenAPI client

- [x] 6.1 Regenerate the typed API client from updated OpenAPI spec (`openapi-typescript`)
- [x] 6.2 Verify generated types include the new endpoints and `is_favorited` field

## 7. Frontend — Favorites store

- [x] 7.1 Create `useFavoritesStore` Pinia store with a set of favorited recipe ids seeded from API responses
- [x] 7.2 Implement `toggleFavorite(recipeId)` with optimistic update and rollback on error

## 8. Frontend — UI components

- [x] 8.1 Add favorite heart toggle button component (active / inactive states)
- [x] 8.2 Integrate toggle button into the recipe card component
- [x] 8.3 Integrate toggle button into the recipe detail page

## 9. Frontend — Favorites page

- [x] 9.1 Create `pages/favorites.vue` with auth guard (redirect to login if unauthenticated)
- [x] 9.2 Fetch `GET /users/me/favorites` and render results using the existing recipe card component
- [x] 9.3 Wire up category and tag filter controls (reuse existing filter components from the main recipe index)
- [x] 9.4 Handle empty state (no favorites yet)

## 10. Frontend — Navigation

- [x] 10.1 Add a "Favorites" link to the nav (visible only when authenticated)
