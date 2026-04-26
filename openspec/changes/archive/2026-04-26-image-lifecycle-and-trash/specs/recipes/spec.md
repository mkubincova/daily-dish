## MODIFIED Requirements

### Requirement: Image upload via Cloudinary signed parameters

The system SHALL provide an authenticated endpoint that returns Cloudinary
signed upload parameters (timestamp, signature, upload preset, and any
required public params). The Cloudinary API secret SHALL never leave the
backend. The frontend SHALL hold the selected file in local state and only
upload to Cloudinary at form-submit time, not on file pick. After the browser
uploads directly to Cloudinary, the frontend SHALL pass the resulting
`secure_url` and `public_id` back to the backend when creating or updating
the recipe, where they are stored as `image_url` and `image_public_id`.

When a PATCH request changes `image_public_id` to a different non-null value,
the backend SHALL destroy the previous Cloudinary asset (via the Destroy API)
after the DB write succeeds. If Destroy fails, the error SHALL be logged and
the response SHALL still succeed — a leaked asset is preferred over a failed
save.

#### Scenario: Authenticated user requests upload signature

- **WHEN** an authenticated user requests upload signing parameters
- **THEN** the system generates a fresh signature server-side using the
  Cloudinary API secret and returns the signed parameters to the client

#### Scenario: Unauthenticated user requests upload signature

- **WHEN** an unauthenticated request hits the upload-sign endpoint
- **THEN** the system responds with HTTP 401

#### Scenario: Recipe update persists Cloudinary image data

- **WHEN** the owner updates a recipe with `image_url` and
  `image_public_id` from a successful Cloudinary upload
- **THEN** the system stores both fields on the recipe and returns them on
  subsequent reads

#### Scenario: Image upload does not occur on file pick

- **WHEN** the user selects an image file in the recipe form
- **THEN** the file is held in local component state and no Cloudinary upload
  is initiated until the user submits the form

#### Scenario: Previous image is destroyed when replaced on update

- **WHEN** the owner submits a PATCH with a new `image_public_id` that differs
  from the current value
- **THEN** the system saves the new image fields, then calls Cloudinary Destroy
  for the old `image_public_id`

#### Scenario: Cloudinary Destroy fails on image replacement

- **WHEN** the PATCH succeeds but the Cloudinary Destroy call for the old
  image errors
- **THEN** the system logs the error with the old `image_public_id` and
  returns the updated recipe normally (HTTP 200)
