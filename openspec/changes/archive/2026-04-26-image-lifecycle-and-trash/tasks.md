## 1. Backend — Cloudinary destroy helper

- [x] 1.1 Add `_destroy_cloudinary_image(public_id: str)` async helper in `uploads.py` that calls the Cloudinary Destroy API using credentials from config; log errors instead of raising
- [x] 1.2 Add `cloudinary` (or `cloudinary-python`) package via `uv add` if not already present; verify Cloudinary credentials are in `config.py`

## 2. Backend — image replacement cleanup on PATCH

- [x] 2.1 In `recipes.py` PATCH handler, capture the recipe's current `image_public_id` before applying updates
- [x] 2.2 After the DB commit, if `image_public_id` changed to a different non-null value, call `_destroy_cloudinary_image` with the old id

## 3. Backend — trash / restore / permanent-delete endpoints

- [x] 3.1 Add `GET /me/recipes/trashed` endpoint returning soft-deleted recipes for the current user, ordered by `deleted_at` desc
- [x] 3.2 Add `POST /recipes/{recipe_id}/restore` endpoint: 404 if not found/not owner, 409 if not soft-deleted, else sets `deleted_at = null` and returns the recipe
- [x] 3.3 Add `DELETE /recipes/{recipe_id}/permanent` endpoint: 404 if not found/not owner, 409 if `deleted_at` is null, else hard-deletes the row then calls `_destroy_cloudinary_image` if `image_public_id` is set
- [x] 3.4 Write Pytest tests covering: list trashed (empty + with items), restore (success, 409 on active recipe, 403 on non-owner), permanent delete (with image, without image, Cloudinary failure path, 409 on active recipe)

## 4. Frontend — defer image upload to form submit

- [x] 4.1 In `RecipeForm.vue`, replace the `@change="uploadImage"` handler with a handler that stores the selected `File` in a `pendingFile` ref (no Cloudinary call yet)
- [x] 4.2 In the form submit handler (`handleSubmit`), if `pendingFile` is set: call `/uploads/sign`, upload the file to Cloudinary, then assign `form.image_url` and `form.image_public_id` from the response before posting/patching the recipe
- [x] 4.3 Update the image preview to use a local object URL (`URL.createObjectURL`) for the pending file, falling back to `form.image_url` for existing images
- [x] 4.4 Clear `pendingFile` and revoke the object URL after successful submit

## 5. Frontend — OpenAPI client regeneration

- [x] 5.1 Regenerate the typed API client (`openapi-typescript`) after the new backend endpoints are in place; fix any type errors that arise in the frontend

## 6. Frontend — trash page

- [x] 6.1 Create `apps/web/app/pages/me/trash.vue` with auth guard (redirect to login if unauthenticated)
- [x] 6.2 Fetch `GET /me/recipes/trashed` on mount and render the list; show recipe title, `deleted_at` date, and Recover / Delete Permanently actions
- [x] 6.3 Wire Recover button to `POST /recipes/{id}/restore`; on success remove from list and show a brief confirmation
- [x] 6.4 Wire Delete Permanently button: show a confirmation dialog, then call `DELETE /recipes/{id}/permanent`; on success remove from list
- [x] 6.5 Add empty state when no trashed recipes exist
- [x] 6.6 Add a "Trash" link on the `/me` page (below the recipe list) linking to `/me/trash`
