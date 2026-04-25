## Context

The app has a recipe list with category/tag filtering and a recipe detail page, but no way for a logged-in user to save recipes they want to revisit. This change adds a `user_favorites` join table, three new API endpoints, and a `/favorites` frontend page that reuses the same filter controls as the main recipe index. The `recipes` list response gains an `is_favorited` boolean for authenticated callers (additive, no breaking change).

## Goals / Non-Goals

**Goals:**
- Authenticated users can toggle favorite on any non-deleted recipe.
- `GET /users/me/favorites` returns the user's favorited recipes with the same category/tag filter support as the main recipe list.
- Recipe list and detail responses include `is_favorited` for authenticated callers.
- A `/favorites` page renders the user's favorites with filtering; redirects unauthenticated users to login.

**Non-Goals:**
- Public or shareable favorites lists.
- Favoriting content other than recipes (e.g. ingredients, tags).
- Favorite counts visible to other users.
- Sorting favorites by anything other than the time they were favorited (`created_at` desc).

## Decisions

### 1. Join table (`user_favorites`) over a column on `recipes`

**Chosen:** A dedicated `user_favorites` table with columns `(id UUIDv7, user_id, recipe_id, created_at)` and a unique constraint on `(user_id, recipe_id)`.

**Alternative considered:** A JSONB array of user ids stored on `recipes`. Rejected because querying "all recipes a user has favorited" becomes expensive and the array grows unboundedly with users.

**Rationale:** The join table is the standard relational approach; it scales, it's trivially indexed, and it maps naturally to the existing UUIDv7 + Alembic migration pattern.

### 2. `is_favorited` injected in recipe list/detail responses (not a separate endpoint)

**Chosen:** When an authenticated user calls `GET /recipes` or `GET /recipes/{slug}`, the response includes `is_favorited: bool`. Unauthenticated callers receive `is_favorited: null` (or field omitted).

**Alternative considered:** A separate `GET /recipes/{id}/favorited` endpoint the frontend polls per card. Rejected because it multiplies HTTP round trips and complicates the client.

**Rationale:** Embedding `is_favorited` avoids N+1 requests. A single LEFT JOIN against `user_favorites` on the list query is cheap, gated behind the authenticated path.

### 3. Favorites list reuses existing recipe filter logic

**Chosen:** `GET /users/me/favorites` accepts the same `category_items` and `tags` query parameters as the public recipe list, with identical OR-within / AND-across semantics.

**Alternative considered:** A simplified favorites page with no filtering. Rejected because the proposal explicitly requires parity with the main recipe index, and the filter logic is already implemented and spec'd.

**Rationale:** The SQL change is a one-line JOIN swap; reusing the filter layer avoids duplicating tested logic.

### 4. Frontend state: Pinia composable for favorite toggling

**Chosen:** A `useFavorites` Pinia store / composable tracks the current user's set of favorited recipe ids in memory. Toggle calls hit the API optimistically, rolling back on error.

**Alternative considered:** Refetch the full recipe list after each toggle. Rejected because it causes visible flicker on the favorites page when removing an item.

**Rationale:** Optimistic UI is the standard pattern for toggle actions; the store is the right layer for cross-page state in this Pinia-first codebase.

## Risks / Trade-offs

- **N+1 on `is_favorited` in recipe list** → Mitigation: resolve with a single `WHERE recipe_id = ANY(:ids)` subquery or a JOIN rather than per-row queries; enforce in code review.
- **Stale `is_favorited` after toggling on detail page, then navigating to list** → Mitigation: the Pinia store is the source of truth after initial load; list response bootstraps it, subsequent toggles update the store directly.
- **Unique-constraint violation on double-favorite** → Mitigation: the `POST /recipes/{id}/favorite` endpoint returns 200 (idempotent) if the row already exists rather than 409.
- **Soft-deleted recipes appearing in favorites** → Mitigation: `GET /users/me/favorites` filters `deleted_at IS NULL` same as other list endpoints.
