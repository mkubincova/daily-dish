## Why

The web app ships with no site metadata: the browser tab shows the default Nuxt title and a generic Nuxt favicon. For a portfolio project that links out from a CV, that first impression is wrong — visitors landing on `dailydish.app` (or whatever the hosted URL becomes) should see "Daily Dish", a recognisable icon, and a sentence describing what the app does. The same metadata also drives link previews when the URL is shared or pasted into Slack, iMessage, etc.

## What Changes

- Set a global `<title>` ("Daily Dish") and meta `description` via Nuxt's `app.head` config, with per-page overrides where useful (recipe pages should use the recipe name).
- Replace the default Nuxt favicon (`apps/web/public/favicon.ico`) with the pre-generated dish-emoji icon set under `apps/web/favicon_io 2/` (Twemoji `1f958.svg`, the shallow-pan-of-food 🥘 glyph, CC-BY 4.0). This is the same glyph already used as the recipe-card image fallback (`apps/web/app/components/RecipeCard.vue:45`).
- Add Open Graph and Twitter Card meta tags so shared links render with title, description, and image.
- Set `lang="en"` on `<html>` and a `theme-color` matching the brand background.

## Capabilities

### New Capabilities
- `site-metadata`: site-wide HTML head metadata (title, description, favicon, social-share tags) and the per-page override mechanism for recipe pages.

### Modified Capabilities
<!-- None — no existing capability owns head metadata today. -->

## Impact

- `apps/web/nuxt.config.ts` — extend `app.head` with title/description/meta/icon links.
- `apps/web/public/` — replace `favicon.ico`; copy in the pre-generated PNG icon variants (16, 32, 180, 192, 512) and `site.webmanifest` from `apps/web/favicon_io 2/`; add an Open Graph share image.
- `apps/web/app/pages/r/[slug]/index.vue` — call `useHead`/`useSeoMeta` to override title and description from the loaded recipe.
- No backend, DB, or API changes. No new runtime dependencies expected (Nuxt's built-in `useHead`/`useSeoMeta` cover the requirement).
