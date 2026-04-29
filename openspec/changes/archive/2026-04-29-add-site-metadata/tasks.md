## 1. Favicon & share-image assets

- [x] 1.1 Copy the seven asset files from `apps/web/favicon_io 2/` into `apps/web/public/`, overwriting the existing default-Nuxt `favicon.ico`:
  - `favicon.ico`
  - `favicon-16x16.png`
  - `favicon-32x32.png`
  - `apple-touch-icon.png`
  - `android-chrome-192x192.png`
  - `android-chrome-512x512.png`
  - `site.webmanifest`

  From the repo root, this is:

  ```sh
  cp "apps/web/favicon_io 2/favicon.ico" \
     "apps/web/favicon_io 2/favicon-16x16.png" \
     "apps/web/favicon_io 2/favicon-32x32.png" \
     "apps/web/favicon_io 2/apple-touch-icon.png" \
     "apps/web/favicon_io 2/android-chrome-192x192.png" \
     "apps/web/favicon_io 2/android-chrome-512x512.png" \
     "apps/web/favicon_io 2/site.webmanifest" \
     apps/web/public/
  ```

  Do NOT copy `about.txt` — its content is captured by the README attribution in 1.4.

- [x] 1.2 Verify in DevTools that `/favicon.ico` returns the dish-emoji icon (not the default Nuxt mark) and that each of the six PNGs is reachable at its `/`-relative path.
- [x] 1.3 Open `apps/web/public/site.webmanifest` and set `name` to "Daily Dish", `short_name` to "Daily Dish", `theme_color` to `#E8DEC8`, and `background_color` to `#E8DEC8`. Leave the icon entries as generated.
- [x] 1.4 Add a one-line Twemoji CC-BY 4.0 attribution to the project README (source: `apps/web/favicon_io 2/about.txt` — Twemoji `1f958.svg`).
- [x] 1.5 Create `apps/web/public/og-image.png` (1200×630) — the dish emoji on the brand background with a "Daily Dish" wordmark in the project's display font. (Not part of the pre-generated set.)
- [x] 1.6 Once 1.1–1.5 are complete and verified, delete the staging folder: `rm -rf "apps/web/favicon_io 2"`. Confirm via `git status` that the only remaining changes under `apps/web/` are inside `apps/web/public/` and the README.

## 2. Default site metadata in `nuxt.config.ts`

- [x] 2.1 In `apps/web/nuxt.config.ts`, extend `app.head` with `htmlAttrs: { lang: "en" }`.
- [x] 2.2 Add the icon `link` entries — `icon` for `/favicon.ico`, `icon` with `sizes="16x16"` and `sizes="32x32"` for the PNGs, `apple-touch-icon` for `/apple-touch-icon.png`, and `manifest` for `/site.webmanifest` — plus a `meta` entry for `theme-color` set to `#E8DEC8` (the `dish-bg` token).
- [x] 2.3 Add `runtimeConfig.public.siteUrl` (default `http://localhost:3000`, overridden by `NUXT_PUBLIC_SITE_URL` in production).
- [x] 2.4 Add a `~/app.vue`-level (or `default` layout) `useSeoMeta` call that sets defaults: `title: "Daily Dish"`, a one-sentence `description`, `ogTitle`, `ogDescription`, `ogImage` (absolute URL using `siteUrl`), `ogType: "website"`, `ogUrl`, `twitterCard: "summary_large_image"`, `twitterTitle`, `twitterDescription`, `twitterImage`.
- [x] 2.5 Manually verify (View Source) on `/` that title is "Daily Dish", description is non-empty, all OG/Twitter tags are present, `<html lang="en">` is set, and `theme-color` is present.

## 3. Per-recipe overrides

- [x] 3.1 In `apps/web/app/pages/r/[slug]/index.vue`, after the recipe data resolves, call `useSeoMeta` with `title: \`${recipe.name} · Daily Dish\``and`description: recipe.description ?? "A recipe from Daily Dish."`.
- [x] 3.2 Mirror the same values into `ogTitle`, `ogDescription`, `twitterTitle`, `twitterDescription`, and set `ogUrl` to the absolute recipe URL (composed from `siteUrl` + `route.path`).
- [x] 3.3 Manually verify on a real recipe page that the tab title shows `<recipe name> · Daily Dish` and View Source shows the recipe-specific description.
- [x] 3.4 Manually verify on a non-existent slug that the page falls back to the global "Daily Dish" title (i.e. the override doesn't run on error).

## 4. Verification

- [x] 4.1 Run a link-preview check: paste the local URL (or a tunneled URL) into a tool like opengraph.xyz / metatags.io and confirm title, description, and image render correctly for both home and a recipe page.
- [x] 4.2 Hard-refresh the browser and confirm the new favicon shows in the tab strip on Chrome and Safari.
- [x] 4.3 Run `pnpm lint` (or the project's equivalent) and `pnpm test` in `apps/web/` to confirm nothing regressed.
