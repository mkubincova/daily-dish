## 1. Backend — schema and seed

- [x] 1.1 Add `Category`, `CategoryItem`, `Tag` SQLModel models with text PKs for the first two and UUIDv7 PK for `Tag`
- [x] 1.2 Add `RecipeCategoryItem` and `RecipeTag` association SQLModels with composite PKs
- [x] 1.3 Add `categories` and `tags` relationships to the `Recipe` model
- [x] 1.4 Generate Alembic migration: create five tables, indexes on the join tables' second columns, `UNIQUE(name)` on `tags`
- [x] 1.5 Extend the same migration with seed inserts: `dish_type` (soup, salad, main, side, dessert, snack); `mood` (light, vegetarian, spicy, hearty, fried); `protein` (beef, chicken, pork, fish, rabbit, duck, turkey, plant_based)
- [x] 1.6 Apply migration locally; verify schema matches and seed rows are present

## 2. Backend — categories endpoint

- [x] 2.1 Add `Category` and `CategoryItem` Pydantic response shapes (id-only — no labels, positions, icons)
- [x] 2.2 Add `GET /categories` router returning categories with nested items
- [x] 2.3 Tests: anonymous read returns expected shape; payload contains no display fields

## 3. Backend — tags endpoint

- [x] 3.1 Add `Tag` Pydantic response shape (`id`, `name`)
- [x] 3.2 Add `GET /tags` returning all tags ordered by `name`
- [x] 3.3 Add `POST /tags` (auth required) with normalisation helper (`lowercase + trim + collapse internal whitespace`)
- [x] 3.4 `POST /tags` returns existing tag (200) on collision; inserts new (201) otherwise; 422 on empty name; 401 unauth
- [x] 3.5 Tests: normalisation cases, idempotency on existing name, auth gate, empty-name rejection

## 4. Backend — recipe write endpoints

- [x] 4.1 Extend `RecipeCreate` and `RecipeUpdate` Pydantic models with `category_item_ids: list[str]` and `tag_ids: list[str]`
- [x] 4.2 Implement attach/replace logic in the recipe service: replace the full association sets atomically on update
- [x] 4.3 Validate every supplied id exists; 422 on unknown category-item or tag references
- [x] 4.4 Extend `RecipeOut` (detail) to include `category_items` (`{id, category_id}` shape) and `tags` (`{id, name}` shape)
- [x] 4.5 Tests: create with categories+tags; update replaces associations; unknown ids 422; soft delete leaves associations intact

## 5. Backend — recipe list filters

- [x] 5.1 Extend `GET /recipes` and `GET /me/recipes` query params: `category_items` (repeatable / comma-list), `tags` (repeatable / comma-list)
- [x] 5.2 Build the SQL filter clause: one `EXISTS (... IN (...))` per repeated parameter group; OR within group, AND across groups
- [x] 5.3 Extend list response item shape to include `category_item_ids` and `tag_ids` per recipe
- [x] 5.4 Add `status` query param to `/me/recipes` (`published` | `draft` | `all`, default `all`)
- [x] 5.5 Cursor invalidation: detect filter change and reset the cursor (or document the chosen behaviour clearly in the handler)
- [x] 5.6 Tests: single-group filter, OR within group, AND across groups, status filter alone and combined, unknown-id returns empty page, anonymous `status` ignored

## 6. Frontend — typed client + composables

- [x] 6.1 Regenerate `openapi-typescript` types from the updated schema
- [x] 6.2 Add composables: `useCategories()` (fetch once, cached), `useTags()` (fetch once, refetch on tag create), `useRecipeFilters()` (URL <-> state)

## 7. Frontend — CategorySidebar component

- [x] 7.1 Create `CategorySidebar.vue` with FE-defined section order config and label/icon map keyed by category and item ids
- [x] 7.2 Render category sections; items inside each section sorted alphabetically by their FE label
- [x] 7.3 Tag chips section: render the tag list, each chip toggles a tag id in the filter state
- [x] 7.4 Bind filter state to route query params (toggle chip → updates URL)
- [x] 7.5 Phone behaviour: collapsible drawer opened by a floating action button anchored bottom-right of the feed (persistent during scroll)
- [x] 7.6 Render the empty-state string `"No recipes found."` from the parent feed when the list response is empty

## 8. Frontend — wire feeds

- [x] 8.1 Mount `CategorySidebar` on the homepage; pass URL query into the recipe list request
- [x] 8.2 Mount `CategorySidebar` on `/me`; add the extra "status" group (Published / Draft / All)
- [x] 8.3 Verify the empty-state string renders on both feeds when filters yield no results

## 9. Frontend — RecipeForm

- [x] 9.1 Add multi-select inputs per category, sourced from `useCategories()`, sorted alphabetically by FE label
- [x] 9.2 Add tag typeahead bound to `useTags()`; "Create '<query>'" appears as the last suggestion when no exact match exists
- [x] 9.3 Selecting "Create" POSTs `/tags` then attaches the returned id; show inline error on POST failure
- [x] 9.4 On submit, send `category_item_ids` and `tag_ids` to the recipe create/update endpoint
- [x] 9.5 Edit mode: pre-populate selected categories and tags from the recipe payload

## 10. Tests and polish

- [x] 10.1 Backend pytest suite green; ruff clean
- [x] 10.2 Frontend Vitest unit tests for `CategorySidebar` filter-toggle behaviour
- [x] 10.3 Manually exercise homepage and `/me` on desktop and a phone viewport (sidebar drawer)
