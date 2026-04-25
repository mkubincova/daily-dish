## Why

Logged-in users have no way to bookmark recipes they love. As the recipe collection grows, rediscovering a favourite requires re-browsing or remembering its title — a friction that makes the app less useful for day-to-day meal planning.

## What Changes

- Users can toggle a **favorite** on any recipe (add / remove).
- A new **Favorites page** lists the current user's favorited recipes.
- The Favorites page supports the same **filtering** (category, tags, search) already available on the main recipes index.
- Favorite state is visible on recipe cards and the recipe detail page.
- Only the authenticated user's own favorites are accessible; unauthenticated users see no favorites UI.

## Capabilities

### New Capabilities

- `recipe-favorites`: Allows logged-in users to save and unsave recipes as favorites, retrieve their favorites list, and filter/search within it.

### Modified Capabilities

- `recipes`: Recipe list responses now include a per-recipe `is_favorited` boolean for the current user (authenticated requests only); recipe cards gain a favorite toggle affordance.

## Impact

- **Backend:** New `user_favorites` join table (`user_id`, `recipe_id`). New endpoints: `POST /recipes/{id}/favorite`, `DELETE /recipes/{id}/favorite`, `GET /users/me/favorites`. Recipe list endpoint (`GET /recipes`) gains `is_favorited` in the response when the caller is authenticated.
- **Frontend:** New `favorites.vue` page; recipe card and detail page gain a heart/star toggle. Pinia store updated to track favorite state. OpenAPI client regenerated.
- **Auth dependency:** Favorites are user-scoped; the auth session must be present.
- **No breaking changes** to existing public API responses (is_favorited is additive).
