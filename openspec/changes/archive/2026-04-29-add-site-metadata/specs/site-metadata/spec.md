## ADDED Requirements

### Requirement: Default site title and description
The application SHALL render a default `<title>` of "Daily Dish" and a default meta `description` describing the app, on every page that does not provide its own override.

#### Scenario: Visiting the home page
- **WHEN** a user opens the root URL
- **THEN** the browser tab displays "Daily Dish"
- **AND** the rendered HTML contains a `<meta name="description">` tag with a non-empty description of the app

#### Scenario: Visiting any non-recipe page (e.g. login, 404)
- **WHEN** a user opens a page that does not call its own `useHead`/`useSeoMeta` override
- **THEN** the browser tab displays "Daily Dish"
- **AND** the description meta tag matches the configured default

### Requirement: Per-recipe page title and description override
Recipe detail pages SHALL override the default title with the recipe name (formatted as `"<Recipe name> · Daily Dish"`) and SHALL set the description from a recipe-derived summary.

#### Scenario: Loading a recipe detail page
- **WHEN** a user opens `/r/<slug>` for a recipe named "Roasted Tomato Soup"
- **THEN** the browser tab displays "Roasted Tomato Soup · Daily Dish"
- **AND** the page's meta description reflects the recipe (e.g. its short description, or first ingredients/steps if no description exists)

### Requirement: Favicon uses a dish-type emoji
The site SHALL serve a favicon set rendered from a Twemoji dish-type glyph (🥘, Twemoji `1f958`) — the same glyph used as the recipe-card image fallback — and MUST NOT serve the default Nuxt favicon. The set SHALL include an ICO for legacy browsers, PNGs for modern browsers and iOS, Android home-screen PNGs, and a web manifest.

#### Scenario: Browser requests the favicon
- **WHEN** a browser requests `/favicon.ico` or follows the `<link rel="icon">` tag from the rendered HTML
- **THEN** it receives an icon based on the dish-emoji glyph (not the default Nuxt mark)
- **AND** the icon renders crisply at standard tab sizes (16×16 and 32×32) and at high-DPI sizes (180×180 for iOS, 192×192 and 512×512 for Android)

#### Scenario: Mobile browser reads the web manifest
- **WHEN** a mobile browser requests `/site.webmanifest`
- **THEN** the manifest returns the app name "Daily Dish", a `theme_color` matching the brand background, and references the 192×192 and 512×512 Android PNGs

### Requirement: Open Graph and Twitter Card metadata
The site SHALL emit Open Graph (`og:*`) and Twitter Card (`twitter:*`) meta tags so that links shared in chat apps and social platforms render with title, description, and a preview image.

#### Scenario: Sharing the home URL in a link-unfurling app
- **WHEN** the home URL is parsed by a link previewer (Slack, iMessage, X)
- **THEN** the preview shows the title "Daily Dish", the default description, and a share image
- **AND** the rendered HTML includes `og:title`, `og:description`, `og:image`, `og:type`, `og:url`, `twitter:card`, `twitter:title`, `twitter:description`, and `twitter:image` tags

#### Scenario: Sharing a recipe URL
- **WHEN** a recipe URL is parsed by a link previewer
- **THEN** the `og:title` and `twitter:title` reflect the recipe-specific title
- **AND** the `og:description` and `twitter:description` reflect the recipe-specific description

### Requirement: HTML language and theme color
The rendered HTML SHALL declare `lang="en"` on the `<html>` element and SHALL include a `<meta name="theme-color">` tag whose value matches the brand background colour used by the rest of the UI.

#### Scenario: Inspecting any rendered page
- **WHEN** the rendered HTML is inspected
- **THEN** the `<html>` tag has `lang="en"`
- **AND** a `<meta name="theme-color" content="...">` tag is present
