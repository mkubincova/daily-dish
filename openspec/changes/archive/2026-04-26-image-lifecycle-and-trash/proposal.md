## Why

Cloudinary images are uploaded immediately on file pick and never deleted — abandoned form uploads, image replacements, and recipe deletions all leak images. The soft-delete mechanic also has no user-facing recovery path, making it a hidden implementation detail with no product value.

## What Changes

- **Defer image upload** — `RecipeForm` holds the selected `File` in local state; Cloudinary upload happens only when the user submits the form.
- **Delete replaced images** — when a recipe PATCH changes `image_public_id`, the backend destroys the old Cloudinary asset before saving.
- **Backend Cloudinary delete endpoint** — a shared `DELETE /uploads/{public_id}` endpoint wraps the Cloudinary Destroy API for reuse by the recipes router.
- **Trash endpoints** — three new recipe endpoints: list trashed, restore, permanently delete (hard delete + Cloudinary destroy).
- **Trash view (frontend)** — a `/me/trash` page or tab on `/me` listing soft-deleted recipes with Recover and Delete Permanently actions.

## Capabilities

### New Capabilities

- `recipe-trash`: Soft-deleted recipes are surfaced in a trash view where the user can restore or permanently delete (with image cleanup) each recipe.

### Modified Capabilities

- `recipes`: Upload timing changes (deferred to submit) and image replacement now triggers Cloudinary cleanup; existing PATCH and DELETE behaviour is extended, not replaced.

## Impact

- **Backend:** `apps/api/app/routers/uploads.py` (new delete endpoint), `apps/api/app/routers/recipes.py` (PATCH image cleanup, new trash/restore/permanent-delete endpoints).
- **Frontend:** `apps/web/app/components/RecipeForm.vue` (defer upload to submit), new `/me/trash` page or tab.
- **Cloudinary:** Destroy API called on image replacement and permanent delete — requires `cloudinary_api_secret` already in config.
- **No schema migrations needed** — soft delete (`deleted_at`) and `image_public_id` columns already exist.
- **OpenAPI client** must be regenerated after adding the new endpoints.
