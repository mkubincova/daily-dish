# Daily Dish — UI Guidelines

Reference this file whenever making any UI change in `apps/web/`. These rules preserve the established design system; don't deviate without a deliberate decision.

---

## Design tokens — always use, never hand-roll

Custom tokens live in `tailwind.config.ts` under the `dish-` namespace and in `app/assets/css/main.css` as component-layer classes.

**Colors** — use `dish-*` names, never raw hex:

| Token | Value | Use |
|---|---|---|
| `dish-primary` | teal `#1E7888` | links, active states, accents |
| `dish-primary-light` | `#2898A8` | hover on primary |
| `dish-primary-dark` | `#145A68` | pressed / deeper accent |
| `dish-secondary` | burnt orange `#C85420` | secondary accents |
| `dish-bg` | warm beige `#E8DEC8` | page background |
| `dish-surface` | cream `#F5EFE3` | cards, panels |
| `dish-fg` | near-black `#1C1A18` | text, icons |
| `dish-muted` | warm gray `#BEB09A` | placeholder, helper text |
| `dish-success` | dark green `#2A6838` | confirmations |
| `dish-error` | red `#C02828` | errors, destructive |

Use opacity modifiers for layering: `text-dish-fg/60`, `border-dish-fg/10`, etc.

**Component classes** — prefer these over re-inventing:

- Labels: `.dish-field-label`, `.dish-section-label`
- Inputs: `.dish-input`, `.dish-input-sm`
- Tags/pills: `.dish-tag`
- Buttons: `.dish-btn-primary`, `.dish-btn-secondary`, `.dish-btn-danger`

If a new repeating pattern emerges, add it to `main.css` rather than duplicating utilities.

---

## Typography — three fonts, strict roles

| Font | Class | Role |
|---|---|---|
| Playfair Display (serif) | `font-display` | Headings, titles, hero text |
| Jost (sans) | `font-sans` | Body text (default) |
| DM Mono (mono) | `font-mono` | Labels, tags, metadata, button text |

Mono + uppercase + tiny size is the signature label style: `font-mono text-[10px] uppercase tracking-widest`.

---

## Icons — Phosphor only

Use **`@phosphor-icons/vue`** exclusively. Import named icons (`PhHeart`, `PhList`, etc.) and pass a `weight` prop (`"regular"` | `"bold"` | `"fill"`).

```vue
<PhHeart weight="fill" class="text-dish-secondary" />
```

Do not add any other icon library. Do not use emoji as icons in interactive UI (emoji are acceptable in static category lists like `categoryConfig.ts`).

---

## Component conventions

- **Reuse before creating.** Check `app/components/` for an existing component before writing a new one.
- **Extract when it repeats.** If a pattern appears in two or more places, extract a component.
- **PascalCase filenames** — `RecipeCard.vue`, not `recipe-card.vue`.
- **Props over slots** for simple data (text, booleans). Use slots only for structural variation.
- Keep components focused; a component that needs more than ~150 lines is a signal to split.

---

## Layout & spacing

- Page container: `max-w-6xl mx-auto px-4 md:px-6`
- Section spacing: `space-y-8` inside forms, `gap-4 md:gap-5` in grids
- Recipe grid: `grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3`
- Sidebar: hidden on mobile (drawer pattern), visible at `lg:`
- Sticky header: `sticky top-0 z-40 h-14`

---

## Interaction patterns

Standard hover/active micro-interactions — apply consistently:

```
hover:-translate-y-1.5 hover:shadow-md transition-all duration-300   ← cards
hover:text-dish-primary transition-colors                             ← text links
hover:scale-110 active:scale-90                                       ← icon buttons
```

Transitions: `transition-colors` for color-only, `transition-all duration-300` when transform is involved.

---

## Form pattern

1. Group fields into sections with `.dish-section-label` headings.
2. All field labels use `.dish-field-label`.
3. All inputs/textareas use `.dish-input` (or `.dish-input-sm`).
4. Required fields get `*` in the label.
5. Submit row: right-aligned buttons, separated by `border-t border-dish-fg/10 pt-6`.
6. Danger actions use `.dish-btn-danger`.

---

## Responsive strategy

Mobile-first. Key breakpoints:

- `sm:` (640 px) — grid goes 2-col
- `md:` (768 px) — increased padding
- `lg:` (1024 px) — sidebar appears, drawer hidden

Never hide content from mobile without providing an equivalent (drawer, accordion, etc.).

---

## Animations

Built-in Vue transition classes defined in `main.css`:

| Name | Use |
|---|---|
| `slide-down` | Mobile nav menu |
| `fade` | Overlays / backdrops |
| `slide-up` | Bottom drawers |

Add new transitions here if needed; don't define them inline in components.

---

## What not to do

- Don't use raw hex, RGB, or Tailwind's built-in color palette (blue-500, etc.) — use `dish-*` tokens.
- Don't import a second icon library.
- Don't recreate `.dish-input` / `.dish-btn-*` inline — use the component classes.
- Don't add Google Fonts links directly in a component — they are loaded globally in `nuxt.config.ts`.
- Don't use `style=""` for anything that can be expressed with Tailwind utilities or `dish-*` tokens.
