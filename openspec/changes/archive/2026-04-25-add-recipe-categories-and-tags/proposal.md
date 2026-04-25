## Why

Recipes today have no classification beyond their title and ingredients,
so the only way to find one is scrolling the chronological feed. As the
recipe set grows, both the public visitor and the owner need a way to
narrow the list down to "spicy vegetarian soups" or "weeknight chicken
mains". The predecessor app shipped a fixed category dropdown; this
change replaces that idea with two complementary primitives — curated
categories for stable taxonomy and freeform tags for everything else.

## What Changes

- Introduce a curated **categories** taxonomy, seeded via Alembic. Each
  category (e.g. `dish_type`) has many `category_items` (e.g. `soup`,
  `salad`, `main`). v1 ships three categories: `dish_type`, `mood`,
  `protein`. No write endpoints — new categories or items are added
  via new migrations during this iteration phase.
- Introduce a freeform **tags** primitive. Any logged-in user can create
  a tag. Tag names are normalised (lowercased, trimmed, internal
  whitespace collapsed) and unique — duplicates resolve to the existing
  tag rather than creating a new one.
- Attach categories and tags to recipes via M2M tables
  (`recipe_category_items`, `recipe_tags`).
- Extend the recipe write endpoints (`POST /recipes`, `PATCH /recipes/{id}`)
  to accept `category_item_ids` and `tag_ids`. Recipe read responses
  include both arrays.
- Extend the recipe list endpoints (`GET /recipes`, `GET /me/recipes`)
  with filter query parameters. Filter semantics: **OR within a key,
  AND across keys**. The owner-only list also accepts a `status`
  filter (`published` / `draft` / `all`).
- Add a `CategorySidebar` component to the homepage and `/me`. Persistent
  on desktop, collapsible drawer on phone. Filter state is URL-driven
  for shareable links and back/forward navigation.
- Update `RecipeForm` with multi-select inputs per category and a tag
  typeahead with a "Create '<query>'" affordance for new tags.

## Capabilities

### New Capabilities
- `categories-and-tags`: the taxonomy itself — categories, category items,
  tags, their normalisation rules, and the read/create endpoints that
  expose them.

### Modified Capabilities
- `recipes`: list endpoints gain filter parameters; create/update accept
  category-item and tag references; read responses include the attached
  categories and tags; owner list gains a `status` filter.

## Impact

- **Schema:** four new tables (`categories`, `category_items`,
  `recipe_category_items`, `tags`, `recipe_tags`) and an Alembic
  migration that also seeds the v1 category/item rows.
- **Backend:** new `categories` and `tags` routers; recipe router
  changes for filter params and write payload extensions; new SQLModel
  models and Pydantic response shapes; OpenAPI surface grows.
- **Frontend:** new `CategorySidebar` component; updates to home and
  `/me` pages to render it and react to URL query state; updates to
  `RecipeForm` for the multi-select and tag typeahead; FE-side label
  maps for category and item ids (i18n-ready, English-only in v1).
- **Out of scope (sibling changes to follow):** free-text search
  (`add-recipe-search` using `pg_trgm`), saved favorites
  (`add-recipe-favorites`), and an admin UI for managing the category
  taxonomy. No admin role / permissions model is introduced here.
