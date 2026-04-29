import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.favorite import UserFavorite
from app.models.recipe import Recipe
from app.models.user import User
from app.utils.uuid7 import new_uuid7


async def _make_recipe(
    session: AsyncSession, user: User, *, is_public: bool = True, deleted: bool = False
) -> Recipe:
    from datetime import UTC, datetime

    recipe = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="Test Recipe",
        slug=f"test-recipe-{new_uuid7()}",
        is_public=is_public,
        deleted_at=datetime.now(UTC) if deleted else None,
    )
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    return recipe


# ---------------------------------------------------------------------------
# POST /recipes/{id}/favorite
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_favorite(auth_client: AsyncClient, session: AsyncSession, user: User):
    recipe = await _make_recipe(session, user)
    resp = await auth_client.post(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 200
    assert resp.json()["is_favorited"] is True

    # Row exists in DB
    fav = await session.exec(
        __import__("sqlmodel", fromlist=["select"])
        .select(UserFavorite)
        .where(
            UserFavorite.user_id == user.id,
            UserFavorite.recipe_id == recipe.id,
        )
    )
    assert fav.first() is not None


@pytest.mark.asyncio
async def test_add_favorite_idempotent(auth_client: AsyncClient, session: AsyncSession, user: User):
    recipe = await _make_recipe(session, user)
    await auth_client.post(f"/api/recipes/{recipe.id}/favorite")
    resp = await auth_client.post(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 200
    assert resp.json()["is_favorited"] is True


@pytest.mark.asyncio
async def test_add_favorite_unauthenticated(client: AsyncClient, session: AsyncSession, user: User):
    recipe = await _make_recipe(session, user)
    resp = await client.post(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_add_favorite_deleted_recipe(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user, deleted=True)
    resp = await auth_client.post(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /recipes/{id}/favorite
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_remove_favorite(auth_client: AsyncClient, session: AsyncSession, user: User):
    recipe = await _make_recipe(session, user)
    session.add(UserFavorite(user_id=user.id, recipe_id=recipe.id))
    await session.commit()

    resp = await auth_client.delete(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_remove_favorite_not_existing_is_idempotent(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user)
    resp = await auth_client.delete(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_remove_favorite_unauthenticated(
    client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user)
    resp = await client.delete(f"/api/recipes/{recipe.id}/favorite")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /users/me/favorites
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_favorites_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/users/me/favorites")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_favorites_returns_favorited_recipes(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    r1 = await _make_recipe(session, user)
    r2 = await _make_recipe(session, user)
    session.add(UserFavorite(user_id=user.id, recipe_id=r1.id))
    await session.commit()

    resp = await auth_client.get("/api/users/me/favorites")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == r1.id
    assert data["items"][0]["is_favorited"] is True
    assert all(item["id"] != r2.id for item in data["items"])


@pytest.mark.asyncio
async def test_list_favorites_excludes_soft_deleted(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user, deleted=True)
    session.add(UserFavorite(user_id=user.id, recipe_id=recipe.id))
    await session.commit()

    resp = await auth_client.get("/api/users/me/favorites")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_list_favorites_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/users/me/favorites")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# is_favorited in recipe list and detail responses
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_recipe_list_is_favorited_for_authenticated(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    r1 = await _make_recipe(session, user)
    r2 = await _make_recipe(session, user)
    session.add(UserFavorite(user_id=user.id, recipe_id=r1.id))
    await session.commit()

    resp = await auth_client.get("/api/recipes")
    assert resp.status_code == 200
    items = {item["id"]: item for item in resp.json()["items"]}
    assert items[r1.id]["is_favorited"] is True
    assert items[r2.id]["is_favorited"] is False


@pytest.mark.asyncio
async def test_recipe_list_is_favorited_null_for_anonymous(
    client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user)
    resp = await client.get("/api/recipes")
    assert resp.status_code == 200
    items = resp.json()["items"]
    matching = [i for i in items if i["id"] == recipe.id]
    assert len(matching) == 1
    assert matching[0]["is_favorited"] is None


@pytest.mark.asyncio
async def test_recipe_detail_is_favorited_for_authenticated(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user)
    session.add(UserFavorite(user_id=user.id, recipe_id=recipe.id))
    await session.commit()

    resp = await auth_client.get(f"/api/recipes/{recipe.slug}")
    assert resp.status_code == 200
    assert resp.json()["is_favorited"] is True


@pytest.mark.asyncio
async def test_recipe_detail_is_favorited_false_when_not_in_favorites(
    auth_client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user)
    resp = await auth_client.get(f"/api/recipes/{recipe.slug}")
    assert resp.status_code == 200
    assert resp.json()["is_favorited"] is False


@pytest.mark.asyncio
async def test_recipe_detail_is_favorited_null_for_anonymous(
    client: AsyncClient, session: AsyncSession, user: User
):
    recipe = await _make_recipe(session, user)
    resp = await client.get(f"/api/recipes/{recipe.slug}")
    assert resp.status_code == 200
    assert resp.json()["is_favorited"] is None
