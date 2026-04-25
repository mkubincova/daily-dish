## Context

The `recipes` table currently has no classification beyond title and
ingredient names. The list endpoints return a flat reverse-chronological
feed. Owners and visitors will increasingly need to narrow the feed
("spicy vegetarian soups", "weeknight chicken mains").

The predecessor app shipped a single fixed category dropdown. After
discussion in `/opsx:explore`, the design splits classification into two
distinct primitives because they have different lifecycles, different
write permissions, and different UI affordances:

- A small **curated taxonomy** (categories + items) that the author
  manages. Stable, browseable, sidebar-driven.
- A **flat freeform tag** primitive that any logged-in user can extend.
  Open-ended, normalised, also filterable.

This design is also the foundation for two follow-on changes —
`add-recipe-search` (pg_trgm full-text-ish search across the same feed)
and `add-recipe-favorites` (a separate /me/favorites collection) — so it
should leave clean integration points for both without anticipating
their detail.

## Goals / Non-Goals

**Goals:**

- Let any user filter the public feed and `/me` by structured
  categories and freeform tags from a sidebar.
- Keep the backend "data product" minimal: stable identifiers only,
  no display labels, icons, colors, or translations.
- Allow the curated taxonomy to grow over time without a code change
  to consumers (just an Alembic migration / seed update).
- Make filter state shareable via URL (deep-linkable, back/forward
  works).
- Lay schema groundwork that both `add-recipe-search` and
  `add-recipe-favorites` can build on without rework.

**Non-Goals:**

- An admin UI for category/tag management. Admin write paths and any
  permissions/role model are deferred.
- Free-text search (next change).
- Saving recipes to a personal collection (third change).
- I18n implementation. The data shape is i18n-ready but v1 ships
  English labels only.
- Hierarchical categories ("European > Slovak"). Flat is enough.

## Decisions

### Decision 1 — Two tables, not one with an `is_freeform` flag

The earlier design considered a single `tags` table with a `facet_id`
column and an `is_freeform` boolean per facet. Rejected in favour of
two clearly separated primitives.

- **Why:** Categories and tags differ along three axes — write
  permission (admin vs any user), lifecycle (curated vs free growth),
  and UI affordance (multi-select dropdown vs typeahead with create).
  Encoding all three differences into a flag on a shared table would
  make every endpoint and component branch on that flag. Two tables
  put the difference in the schema where it belongs.
- **Alternative considered:** unified `tags` table with `facet_id` and
  `is_freeform`. Cheaper schema, more expensive code. Loses clarity
  about who can write what.

### Decision 2 — Text primary keys for `categories` and `category_items`

Both tables use stable text identifiers (`'dish_type'`, `'soup'`)
instead of synthetic UUID PKs.

- **Why:** The whole point of these rows is to be the stable key the
  frontend uses to look up labels, icons, and translations. A UUID
  would force a parallel `slug` column that does the same job, plus
  a join in queries. Text PKs collapse the two into one.
- **Alternative considered:** UUIDv7 PK + unique `slug` text column.
  Matches the project convention used elsewhere. Rejected because
  the convention exists to avoid enumeration leaks on user-owned
  data — categories are not user data and have no enumeration risk.

### Decision 3 — UUIDv7 for `tags`

Tags use UUIDv7 even though their `name` is also unique.

- **Why:** Tags are user-created and user-renameable in spirit
  (lowercase normalisation may collapse two writes into one). Stable
  ids decouple "what the tag is called right now" from "the recipes
  attached to it". Renames stay cheap.
- **Alternative considered:** text PK on the normalised name. Cheaper
  but every potential future rename becomes a cascade-update.

### Decision 4 — Tag name normalisation: lowercase, trim, collapse internal whitespace

Normalisation runs in the API layer before insert and lookup.

- **Why:** Single author or not, the FE typeahead will fall back to
  "Create '<query>'" the moment a casing or whitespace variant slips
  through. Normalising defensively keeps the namespace tight without
  imposing it on the UX (the user types whatever; the system stores
  the normalised form).
- **Rules:** `name = " ".join(input.strip().lower().split())`. So
  `"  Spicy   "` and `"SPICY"` both become `"spicy"`.
- **Alternative considered:** also strip diacritics. Rejected for v1
  because tag names will mix Slovak and English and stripping `š`→`s`
  would silently merge `pošta` and `posta`. Reconsider with `unaccent`
  if it becomes a problem.

### Decision 5 — `POST /tags` is the only way to create a tag

Recipe writes (`POST /recipes`, `PATCH /recipes/{id}`) accept
`tag_ids` only — never raw tag names. The frontend typeahead is
responsible for hitting `POST /tags` first when the user picks the
"Create '<query>'" option.

- **Why:** Single creation path means a single normalisation
  implementation and a single uniqueness collision handler. The
  alternative pushes "is this a known tag or a new one?" logic into
  the recipe writer, which is the wrong place.
- **`POST /tags` is idempotent on `name`:** if the normalised name
  already exists, return the existing tag (200 OK). Otherwise insert
  and return (201 Created). Race conditions resolve naturally via the
  `UNIQUE(name)` constraint and a single retry-on-conflict.
- **Alternative considered:** `PATCH /recipes/{id}` accepts a mixed
  array of `tag_ids` + new tag name strings. Convenient, but couples
  recipe-write semantics to tag creation and complicates partial
  failure (one tag created, then recipe write fails — orphan).

### Decision 6 — Filter semantics: OR within a key, AND across keys

`?category_items=soup,salad&category_items=vegetarian&tags=<christmas-uuid>`
returns "(soup OR salad) AND vegetarian AND tagged christmas".
Implemented in SQL with one `EXISTS (... WHERE column IN (...))` per key:

```sql
SELECT * FROM recipes r
WHERE EXISTS (
  SELECT 1 FROM recipe_category_items
  WHERE recipe_id = r.id AND category_item_id IN ('soup', 'salad')
) AND EXISTS (
  SELECT 1 FROM recipe_category_items
  WHERE recipe_id = r.id AND category_item_id IN ('vegetarian')
) AND EXISTS (
  SELECT 1 FROM recipe_tags
  WHERE recipe_id = r.id AND tag_id IN ('<christmas-uuid>')
)
```

- **Why this shape:** matches what users mean when they pick chips in
  a faceted sidebar. The query planner handles `EXISTS` well with the
  composite indexes on the join tables.
- **Alternative considered:** AND within and across (intersection of
  every chip). Rejected — picking "soup" and "salad" returning
  recipes that are *both* would always be empty.
- **Alternative considered:** Filter parameters group items by their
  `category_id` automatically (so `category_items=soup,vegetarian` would
  do `(soup OR ...) AND (vegetarian OR ...)`). Rejected because it pushes
  category-membership knowledge into the query layer; explicit
  per-key parameters keep the API self-describing.

### Decision 7 — Filter state lives in the URL

The `CategorySidebar` component is a controlled component bound to
route query params. Toggling a chip updates the URL; the page reacts
to the new query.

- **Why:** Shareable, back/forward works, server-rendered first paint
  on Nuxt SSR sees the same state. Pinia would otherwise need a
  serialiser to do the same job.
- **Alternative considered:** Pinia store + history.replaceState
  side-effect. More moving parts, easy to drift out of sync.

### Decision 8 — FE owns labels, sort order, icons, i18n

Backend returns `[{id: 'dish_type', items: [{id: 'soup'}, ...]}]`.
Nothing else. The frontend has a config map keyed by these ids that
provides labels, icons, sidebar section order, and (eventually)
translations. Items inside a category are rendered alphabetically by
their FE label.

- **Why:** Display is a UI concern that varies by viewport and locale.
  Putting it on the row would conflate two different rates of change
  (taxonomy changes rarely; UI polish changes often).
- **Alternative considered:** `position`, `label`, `icon` columns on
  the rows. Rejected — every label tweak becomes a backend deploy.

### Decision 9 — Pagination resets when filters or query change

The list endpoint returns a cursor for the next page. When filters
change, the FE drops the cursor and starts from the top. Cursor
encodes only ordering position, not filter snapshot.

- **Why:** Simple and correct. Filter changes invalidate the previous
  result set anyway.
- **Alternative considered:** stateful cursor that captures filter
  hash. Premature.

## Risks / Trade-offs

- **Tag spam from non-author users.** With multi-user OAuth, a guest
  signup could create dozens of garbage tags. → Mitigation: tag
  creation is auth-gated and visible per `created_by`. If it becomes
  a real problem, an admin role + soft-delete on tags is a small
  follow-up. Until that lands, the namespace is the author's risk
  to bear.
- **Migration carries seed data.** Mixing schema and seed in one
  Alembic migration is convenient but couples deploys. → Mitigation:
  use a single migration that creates tables and inserts the seed
  rows in a transaction. Future migrations can do additive seeding
  without touching schema.
- **Filter URLs become long.** Five categories × 10 items each + a
  handful of tags can blow past 2KB query strings. → Mitigation: not
  a real risk at v1 catalogue size. If it becomes one, the cursor
  endpoint can accept POST with body and return a short shareable
  token.
- **OR-within-key is a soft commitment.** Once shipped, switching to
  AND-within breaks deep links. → Mitigation: document semantics in
  the spec; a breaking flip would warrant a new query parameter
  (e.g. `mode=all`) rather than redefining the existing one.
- **`status` filter on `/me` overlaps with `is_public`.** The boolean
  on the recipe row means "published"; `status=draft` is the inverse;
  `status=all` is no filter. → Mitigation: implement `status` as a
  thin alias over the existing `is_public` predicate; no schema
  changes.

## Migration Plan

Single Alembic migration that:

1. Creates `categories`, `category_items`, `recipe_category_items`,
   `tags`, `recipe_tags` tables.
2. Adds composite indexes on the join tables (PK already covers
   `(recipe_id, ...)`; add an index on `(category_item_id)` and
   `(tag_id)` for the reverse lookup used by filter `EXISTS` clauses).
3. Adds `UNIQUE(name)` on `tags`.
4. Inserts seed rows for the three v1 categories and the items below.

**Initial seed (locked):**

- `dish_type`: `soup`, `salad`, `main`, `side`, `dessert`, `snack`
- `mood`: `light`, `vegetarian`, `spicy`, `hearty`, `fried`
- `protein`: `beef`, `chicken`, `pork`, `fish`, `rabbit`, `duck`,
  `turkey`, `plant_based`

`protein.plant_based` covers tofu, lentils, beans, etc. Recipes with no
notable protein source simply leave the protein category unset rather
than carrying a "none" item.

No backfill of existing recipes — they start with empty category and
tag arrays and will appear in the unfiltered feed as before.

Rollback is the inverse: `downgrade()` drops the five tables. Existing
recipe rows are untouched.

### Decision 10 — Single generic empty-state message

When the filtered list returns zero recipes, the feed renders the
single string **"No recipes found."** regardless of which filters or
(future) search query produced the empty result.

- **Why:** A single message keeps the component stateless about
  *why* the result is empty. It also future-proofs the copy — when
  `add-recipe-search` lands, the same string covers "filters matched
  nothing", "query matched nothing", and "both combined matched
  nothing" without per-cause branching.
- **Alternative considered:** Tailored messages per cause ("No
  recipes match your filters", "No recipes match '<query>'", "Try
  removing some filters"). More helpful in the abstract but requires
  the empty-state component to know about every input source.
  Diminishing returns for a personal app.

### Decision 11 — Floating action button to open the phone filter drawer

On phone viewports the filter drawer is opened by a floating action
button (FAB) anchored to the bottom-right of the feed, persistent
during scroll, rather than a button at the top of the feed.

- **Why:** The user is scrolling a long recipe list with their thumb;
  a FAB stays in reach the whole time. A top-of-feed button gets
  scrolled away within a viewport and forces a scroll-to-top before
  refining the filter set.
- **Alternative considered:** Top-of-feed "Filters" button next to
  the page heading. Cheaper to build (no fixed positioning, no
  z-index dance with the bottom nav), and matches the desktop
  visual hierarchy. Rejected because the cooking-on-phone use case
  is exactly the one where the FAB pays off.

## Open Questions

_None — all design questions resolved._
