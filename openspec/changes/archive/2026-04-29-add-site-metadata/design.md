## Context

The Nuxt app currently ships with no head metadata: no global title, no description, default Nuxt favicon (`apps/web/public/favicon.ico`), no Open Graph tags, no `theme-color`, and no `lang` attribute. The fix is small in scope but spans configuration, asset generation, and per-page overrides — worth a short design doc to nail the favicon-generation approach and the per-recipe override before coding.

The `🥘` glyph is already established as the brand secondary mark inside the UI: it's the recipe-card image fallback (`apps/web/app/components/RecipeCard.vue:45`), the dish-type category icon (`apps/web/app/components/CategorySidebar.vue:15`), and appears on the recipe detail page (`apps/web/app/pages/r/[slug]/index.vue:70,89`). Reusing it as the favicon makes the app instantly recognisable in a tab strip and avoids a separate asset-design step.

The recipe model already has an optional `description: str | None` field (`apps/api/app/models/recipe.py`), and the recipe detail page already reads it for the lede paragraph (`apps/web/app/pages/r/[slug]/index.vue:166`). That field is the natural source for the per-recipe meta description.

## Goals / Non-Goals

**Goals:**

- Browser tab shows "Daily Dish" + a recognisable icon on every page.
- Recipe pages show the recipe name in the title and a recipe-derived description.
- Shared links unfurl with title, description, and an image in chat apps.
- One configuration change per page that wants an override — no metadata layer/abstraction.

**Non-Goals:**

- A bespoke logo or full brand identity. The dish emoji is the v1 mark.
- Per-recipe Open Graph images (using a generic share image is fine for v1; a dynamic OG-image renderer is a v2 backlog item).
- Internationalisation. `lang="en"` is hardcoded.
- A sitemap, robots policy beyond what already exists, or canonical-URL handling.
- Structured data (JSON-LD `Recipe` schema) — worthwhile but separable; defer to a v2 SEO pass.

## Decisions

### Favicon source: pre-generated PNGs + ICO from Twemoji, not runtime SVG-with-emoji

A pre-generated icon set already exists at `apps/web/favicon_io 2/` (output of a favicon-generator run against Twemoji `1f958.svg`, the shallow-pan-of-food 🥘 glyph, CC-BY 4.0; see `apps/web/favicon_io 2/about.txt`). Ship it as-is into `apps/web/public/`:

- `favicon.ico` — multi-resolution ICO for legacy browsers.
- `favicon-16x16.png`, `favicon-32x32.png` — modern browsers via `<link rel="icon" sizes="…">`.
- `apple-touch-icon.png` — 180×180 PNG for iOS home-screen.
- `android-chrome-192x192.png`, `android-chrome-512x512.png` — referenced by the web manifest for Android home-screen.
- `site.webmanifest` — references the Android PNGs and sets the app name / theme color.
- `og-image.png` — 1200×630 share image (emoji + "Daily Dish" wordmark). NOT included in the pre-generated set; produced separately for this change.

**Alternative considered: also ship an inline SVG icon (`icon.svg`).** Rejected — the pre-generated set doesn't include one, and the PNG + ICO combination already covers every browser/device case in the spec. An SVG would only matter if we wanted the favicon to scale beyond 512px or recolor with `prefers-color-scheme`, neither of which is in scope.

**Alternative considered: ship only an inline SVG data-URI with the emoji glyph.** Rejected because emoji rendering varies wildly by OS — Apple Color Emoji ≠ Noto Emoji ≠ Segoe UI Emoji — so a tab-strip favicon would look different per machine, and Windows/Linux users would often see a flat outline. Pre-rendered Twemoji PNGs give a consistent visual.

**Alternative considered: design a custom logo.** Rejected for v1 — the goal is "stop looking like a default Nuxt scaffold", not a brand exercise. The dish emoji is already the in-app mark, so reusing it is consistent.

**Glyph note:** the favicon uses 🥘 (Twemoji `1f958`, shallow pan of food) — the same glyph as the recipe-card image fallback (`apps/web/app/components/RecipeCard.vue:45`). The recipe detail page (`apps/web/app/pages/r/[slug]/index.vue:70,89`) and the dish-type category icon (`apps/web/app/components/CategorySidebar.vue:15`) still use 🍽️ (`1f37d`); both are dish-type Twemoji glyphs and acceptable for v1. Reconciling the in-app glyphs is out of scope for this change.

**Attribution:** add a one-line Twemoji CC-BY 4.0 attribution to the project README. The licence text already lives in `apps/web/favicon_io 2/about.txt` for reference.

### Where the metadata lives: `nuxt.config.ts` + page-level `useSeoMeta`

Defaults go in `app.head` inside `apps/web/nuxt.config.ts` (extending the existing block). Per-page overrides use `useSeoMeta()` inside the relevant `<script setup>` — Nuxt's recommended primitive, which writes title, description, and the full OG/Twitter set in one call.

**Alternative considered: a `<SeoHead>` wrapper component or composable.** Rejected — only one page (`/r/[slug]`) needs an override today. Adding an abstraction for one call site is premature; revisit if/when category, tag, or search pages also want overrides.

**Alternative considered: Nuxt SEO module (`@nuxtjs/seo`).** Rejected for v1 — pulls in a sitemap/robots/JSON-LD bundle we don't need yet, and the built-in `useSeoMeta` covers everything in the spec. Easy to adopt later if the SEO backlog grows.

### Per-recipe description fallback

Use `recipe.description` when present. When null, fall back to a fixed string ("A recipe from Daily Dish.") rather than synthesising one from ingredients/steps. Synthesising would couple meta-description generation to recipe data shape and risks ugly truncation in previewers.

**Alternative considered: derive from first step or first three ingredients.** Rejected — fragile, may produce nonsense for short or unusual recipes, and adds string-formatting logic to a config-style change.

### Theme color

Use `#E8DEC8` (the `dish-bg` token from `UI_GUIDELINES.md`) so the iOS/Android browser chrome blends into the page background.

**Alternative considered: `dish-surface` (`#F5EFE3`) or the accent terracotta.** Rejected — `dish-bg` is what the page actually paints behind the chrome, so matching it gives the most cohesive look. Accent terracotta would draw attention to chrome that's better left unobtrusive.

### Site URL for absolute `og:url` / `og:image`

Read from `runtimeConfig.public.siteUrl`, defaulting to `http://localhost:3000`. The Vercel deploy sets `NUXT_PUBLIC_SITE_URL` to the production URL.

**Alternative considered: hardcode the production URL.** Rejected — breaks preview deploys and local sharing tests. A runtime config var is one extra line and keeps environments correct.

## Risks / Trade-offs

- **[Emoji licensing]** → Twemoji is CC-BY 4.0; add a one-line attribution to `apps/web/README.md` (or root README). Apple Color Emoji is not redistributable, so do NOT ship a screenshot of an Apple glyph as an asset.
- **[Favicon caching]** → Browsers cache favicons aggressively. Document in tasks that the dev should hard-refresh / clear cache during local verification.
- **[OG image goes stale if branding changes]** → Acceptable. The image is a single PNG; replace it when branding evolves.
- **[`useSeoMeta` on a page that errors]** → If the recipe fetch fails, the page should still render a sensible title (e.g. "Daily Dish" via the global default). Verify by hitting an unknown slug during manual QA.

## Migration Plan

No data migration. Pure frontend asset + config change, deployed by the next Vercel push. Rollback = revert the commit.

## Open Questions

- None blocking. The production site URL needs to be set in Vercel env when the change ships, but that is a deployment step, not a design decision.
