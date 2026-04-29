from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.models.recipe import Recipe
from app.models.user import User
from app.utils.uuid7 import new_uuid7


def _trashed_recipe(user_id: str, **kwargs) -> Recipe:
    return Recipe(
        id=new_uuid7(),
        user_id=user_id,
        title=kwargs.get("title", "Old Recipe"),
        slug=kwargs.get("slug", f"old-recipe-{new_uuid7()[:8]}"),
        is_public=True,
        deleted_at=kwargs.get("deleted_at", datetime.now(UTC) - timedelta(days=1)),
        image_public_id=kwargs.get("image_public_id"),
        image_url=kwargs.get("image_url"),
    )


def _active_recipe(user_id: str, **kwargs) -> Recipe:
    return Recipe(
        id=new_uuid7(),
        user_id=user_id,
        title=kwargs.get("title", "Active Recipe"),
        slug=kwargs.get("slug", f"active-recipe-{new_uuid7()[:8]}"),
        is_public=True,
    )


# ── List trashed ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_trashed_requires_auth(client: AsyncClient):
    resp = await client.get("/api/recipes/trashed")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_trashed_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/recipes/trashed")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_trashed_returns_deleted_recipes(auth_client: AsyncClient, session, user: User):
    r1 = _trashed_recipe(user.id, title="Deleted One", slug="deleted-one-abc")
    r2 = _trashed_recipe(user.id, title="Deleted Two", slug="deleted-two-abc")
    active = _active_recipe(user.id, slug="active-abc")
    session.add_all([r1, r2, active])
    await session.commit()

    resp = await auth_client.get("/api/recipes/trashed")
    assert resp.status_code == 200
    data = resp.json()
    slugs = [r["slug"] for r in data]
    assert "deleted-one-abc" in slugs
    assert "deleted-two-abc" in slugs
    assert "active-abc" not in slugs


@pytest.mark.asyncio
async def test_list_trashed_only_own_recipes(
    auth_client: AsyncClient, session, user: User, other_user: User
):
    mine = _trashed_recipe(user.id, slug="mine-trash-abc")
    theirs = _trashed_recipe(other_user.id, slug="theirs-trash-abc")
    session.add_all([mine, theirs])
    await session.commit()

    resp = await auth_client.get("/api/recipes/trashed")
    slugs = [r["slug"] for r in resp.json()]
    assert "mine-trash-abc" in slugs
    assert "theirs-trash-abc" not in slugs


# ── Restore ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_restore_success(auth_client: AsyncClient, session, user: User):
    recipe = _trashed_recipe(user.id, slug="restore-me-abc")
    session.add(recipe)
    await session.commit()

    resp = await auth_client.post(f"/api/recipes/{recipe.id}/restore")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "restore-me-abc"

    # Verify it's no longer in trash and visible in active list
    trash_resp = await auth_client.get("/api/recipes/trashed")
    slugs = [r["slug"] for r in trash_resp.json()]
    assert "restore-me-abc" not in slugs


@pytest.mark.asyncio
async def test_restore_active_recipe_returns_409(auth_client: AsyncClient, session, user: User):
    recipe = _active_recipe(user.id, slug="active-no-restore")
    session.add(recipe)
    await session.commit()

    resp = await auth_client.post(f"/api/recipes/{recipe.id}/restore")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_restore_other_users_recipe_returns_403(
    auth_client: AsyncClient, session, other_user: User
):
    recipe = _trashed_recipe(other_user.id, slug="others-trash-restore")
    session.add(recipe)
    await session.commit()

    resp = await auth_client.post(f"/api/recipes/{recipe.id}/restore")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_restore_nonexistent_recipe_returns_404(auth_client: AsyncClient):
    resp = await auth_client.post(f"/api/recipes/{new_uuid7()}/restore")
    assert resp.status_code == 404


# ── Permanent delete ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_permanent_delete_without_image(auth_client: AsyncClient, session, user: User):
    recipe = _trashed_recipe(user.id, slug="perm-del-no-img")
    session.add(recipe)
    await session.commit()

    with patch("app.routers.uploads._destroy_cloudinary_image") as mock_destroy:
        resp = await auth_client.delete(f"/api/recipes/{recipe.id}/permanent")

    assert resp.status_code == 204
    mock_destroy.assert_not_called()

    # Confirm it's gone from trash
    trash = await auth_client.get("/api/recipes/trashed")
    assert all(r["id"] != recipe.id for r in trash.json())


@pytest.mark.asyncio
async def test_permanent_delete_with_image(auth_client: AsyncClient, session, user: User):
    recipe = _trashed_recipe(
        user.id,
        slug="perm-del-with-img",
        image_public_id="daily-dish/recipes/abc123",
        image_url="https://res.cloudinary.com/test/image/upload/abc123.jpg",
    )
    session.add(recipe)
    await session.commit()

    with patch(
        "app.routers.uploads._destroy_cloudinary_image", new_callable=AsyncMock
    ) as mock_destroy:
        resp = await auth_client.delete(f"/api/recipes/{recipe.id}/permanent")

    assert resp.status_code == 204
    mock_destroy.assert_called_once_with("daily-dish/recipes/abc123")


@pytest.mark.asyncio
async def test_permanent_delete_cloudinary_failure_still_deletes(
    auth_client: AsyncClient, session, user: User
):
    recipe = _trashed_recipe(
        user.id,
        slug="perm-del-cloud-fail",
        image_public_id="daily-dish/recipes/failme",
    )
    session.add(recipe)
    await session.commit()

    # Patch the underlying SDK call so _destroy_cloudinary_image's error handling runs
    with patch("cloudinary.uploader.destroy", side_effect=Exception("Cloudinary down")):
        resp = await auth_client.delete(f"/api/recipes/{recipe.id}/permanent")

    # Recipe deleted despite Cloudinary failure
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_permanent_delete_active_recipe_returns_409(
    auth_client: AsyncClient, session, user: User
):
    recipe = _active_recipe(user.id, slug="active-no-perm-del")
    session.add(recipe)
    await session.commit()

    resp = await auth_client.delete(f"/api/recipes/{recipe.id}/permanent")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_permanent_delete_other_users_recipe_returns_403(
    auth_client: AsyncClient, session, other_user: User
):
    recipe = _trashed_recipe(other_user.id, slug="others-perm-del")
    session.add(recipe)
    await session.commit()

    resp = await auth_client.delete(f"/api/recipes/{recipe.id}/permanent")
    assert resp.status_code == 403
