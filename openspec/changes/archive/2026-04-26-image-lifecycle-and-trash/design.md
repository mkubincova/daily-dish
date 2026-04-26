## Context

Cloudinary images are currently uploaded eagerly on file pick in `RecipeForm.vue`. This leaks images whenever the user abandons the form, changes their mind, or replaces the image before saving. The backend stores `image_public_id` but never uses it — no deletion happens on recipe update or soft-delete.

Soft-delete was chosen as a non-negotiable architectural decision, but there is no UI for recovery, so the mechanic is invisible to the user and provides no product value. Adding a trash view completes the intent.

## Goals / Non-Goals

**Goals:**
- Defer Cloudinary upload to form submit, eliminating orphaned images from abandoned forms.
- Delete the previous Cloudinary asset when a recipe's image is replaced (via PATCH).
- Surface soft-deleted recipes in a trash view with restore and permanent-delete actions.
- Permanent delete = hard delete from DB + Cloudinary Destroy.

**Non-Goals:**
- Undo/redo within the recipe form.
- Automatic trash expiry (no TTL on soft-deleted recipes in v1).
- Bulk restore or bulk permanent delete.
- Cloudinary Destroy on normal soft-delete (image is preserved so restore is lossless).

## Decisions

### 1. Cloudinary Destroy called from the backend, not the frontend

**Decision:** Add a shared `_destroy_cloudinary_image(public_id)` helper in the backend; call it from the recipes router on PATCH (image replaced) and DELETE permanent.

**Alternative considered:** Frontend calls a `DELETE /uploads/{public_id}` endpoint. Rejected because it opens a user-controlled deletion endpoint that could be abused to destroy any asset by guessing its public_id. Keeping Destroy server-side limits the attack surface — the backend only destroys images that are actually referenced by the requesting user's recipes.

**Alternative considered:** Frontend calls Cloudinary Destroy directly using signed params. Rejected because it exposes the API secret pathway and requires a separate signing step for deletion.

### 2. Upload deferred to form submit (file held in component state)

**Decision:** `RecipeForm` stores the selected `File` in a `pendingFile` ref. On submit, upload to Cloudinary first (calling `/uploads/sign`), then send `image_url` + `image_public_id` with the recipe payload. The existing `uploadImage` function is called from `handleSubmit` instead of the file-input `@change` handler.

**Alternative considered:** Keep eager upload but delete the asset if the form is cancelled/abandoned. Rejected because detecting "abandoned" reliably across navigation, tab close, and cancel button is fragile. Deferred upload is simpler and has no false positives.

### 3. Trash view at `/me/trash` (separate page)

**Decision:** A dedicated `/me/trash` page rather than a tab on `/me`.

**Alternative considered:** Tab switcher on the `/me` page. Rejected to keep the `/me` page focused on active recipes and avoid a more complex tabbed layout for a rarely-used feature.

### 4. PATCH image-replacement atomicity

**Decision:** Destroy the old image *after* the DB update commits successfully. If Destroy fails, log the error but do not roll back — a leaked Cloudinary asset is a better outcome than a failed recipe save.

**Alternative considered:** Destroy before the DB update. Rejected because if the DB write then fails, the asset is gone but `image_public_id` in the DB still points to the deleted asset.

### 5. Permanent delete: DB hard-delete then Cloudinary Destroy

**Decision:** Hard-delete the recipe row first (removing the `deleted_at`-gated soft-deleted record), then call Cloudinary Destroy. If Destroy fails, log but return 204 — the recipe is already gone from the user's perspective.

**Alternative considered:** Cloudinary Destroy first. Rejected: if the DB delete then fails, the image is gone but the recipe is still in the trash — confusing state.

## Risks / Trade-offs

- **Cloudinary Destroy failure leaks assets** → Mitigation: log `public_id` on failure so it can be manually cleaned up; accepted trade-off for UX reliability.
- **Deferred upload adds latency to form submit** → Mitigation: show a loading state during submit; no worse than existing eager upload UX.
- **`/me/trash` is a new route with no link from nav** → Mitigation: add a small "Trash" link on the `/me` page (e.g. below the recipe list) to make it discoverable.
- **No trash expiry** → Accepted for v1. A cron job for auto-expiry can be added later without schema changes.
