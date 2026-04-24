import pytest
from httpx import AsyncClient

from app.deps import SESSION_COOKIE
from app.main import app
from app.models.recipe import Recipe
from app.models.user import User
from app.utils.uuid7 import new_uuid7
from tests.conftest import make_session_cookie

RECIPE_PAYLOAD = {
    "title": "Chocolate Cake",
    "description": "A rich chocolate cake",
    "is_public": True,
    "steps": [{"position": 1, "text": "Mix ingredients"}],
    "ingredients": [{"position": 1, "quantity": "2", "unit": "cups", "name": "flour"}],
}


@pytest.mark.asyncio
async def test_create_recipe_requires_auth(client: AsyncClient):
    resp = await client.post("/recipes", json=RECIPE_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_recipe(auth_client: AsyncClient, user: User):
    resp = await auth_client.post("/recipes", json=RECIPE_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Chocolate Cake"
    assert "slug" in data
    assert data["owner"]["name"] == user.name
    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["name"] == "flour"


@pytest.mark.asyncio
async def test_create_recipe_missing_title(auth_client: AsyncClient):
    resp = await auth_client.post("/recipes", json={"description": "No title"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_public_list_anonymous(client: AsyncClient, session, user: User):
    recipe = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="Public Recipe",
        slug="public-recipe-abc123",
        is_public=True,
    )
    session.add(recipe)
    await session.commit()

    resp = await client.get("/recipes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(r["slug"] == "public-recipe-abc123" for r in data["items"])


@pytest.mark.asyncio
async def test_public_list_excludes_drafts(client: AsyncClient, session, user: User):
    draft = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="Draft Recipe",
        slug="draft-recipe-xyz456",
        is_public=False,
    )
    session.add(draft)
    await session.commit()

    resp = await client.get("/recipes")
    assert resp.status_code == 200
    data = resp.json()
    slugs = [r["slug"] for r in data["items"]]
    assert "draft-recipe-xyz456" not in slugs


@pytest.mark.asyncio
async def test_get_public_recipe_by_slug(client: AsyncClient, session, user: User):
    recipe = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="Visible",
        slug="visible-abc",
        is_public=True,
    )
    session.add(recipe)
    await session.commit()

    resp = await client.get("/recipes/visible-abc")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Visible"


@pytest.mark.asyncio
async def test_get_draft_recipe_anonymous_returns_404(client: AsyncClient, session, user: User):
    recipe = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="Draft",
        slug="draft-secret",
        is_public=False,
    )
    session.add(recipe)
    await session.commit()

    resp = await client.get("/recipes/draft-secret")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_owner_can_see_own_draft(auth_client: AsyncClient, session, user: User):
    recipe = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="My Draft",
        slug="my-draft-111",
        is_public=False,
    )
    session.add(recipe)
    await session.commit()

    resp = await auth_client.get("/recipes/my-draft-111")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_non_owner_cannot_see_draft(session, other_user: User, user: User):
    recipe = Recipe(
        id=new_uuid7(),
        user_id=user.id,
        title="Owner Draft",
        slug="owner-draft-222",
        is_public=False,
    )
    session.add(recipe)
    await session.commit()

    from app.database import get_session

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    cookie = make_session_cookie(other_user.id)

    from httpx import ASGITransport
    from httpx import AsyncClient as AC

    async with AC(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies={SESSION_COOKIE: cookie},
    ) as ac:
        resp = await ac.get("/recipes/owner-draft-222")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_mine_requires_auth(client: AsyncClient):
    resp = await client.get("/recipes/mine")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_mine_includes_drafts(auth_client: AsyncClient, session, user: User):
    pub = Recipe(id=new_uuid7(), user_id=user.id, title="Public", slug="pub-mine-1", is_public=True)
    draft = Recipe(id=new_uuid7(), user_id=user.id, title="Draft", slug="draft-mine-1", is_public=False)
    session.add(pub)
    session.add(draft)
    await session.commit()

    resp = await auth_client.get("/recipes/mine")
    assert resp.status_code == 200
    slugs = [r["slug"] for r in resp.json()]
    assert "pub-mine-1" in slugs
    assert "draft-mine-1" in slugs


@pytest.mark.asyncio
async def test_soft_delete(auth_client: AsyncClient, session, user: User):
    recipe = Recipe(id=new_uuid7(), user_id=user.id, title="To Delete", slug="to-delete-1", is_public=True)
    session.add(recipe)
    await session.commit()

    resp = await auth_client.delete(f"/recipes/{recipe.id}")
    assert resp.status_code == 204

    # Should now be 404
    resp2 = await auth_client.get("/recipes/to-delete-1")
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_non_owner_delete_returns_404(session, other_user: User, user: User):
    recipe = Recipe(id=new_uuid7(), user_id=user.id, title="Protected", slug="protected-1", is_public=True)
    session.add(recipe)
    await session.commit()

    from app.database import get_session

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    cookie = make_session_cookie(other_user.id)

    from httpx import ASGITransport
    from httpx import AsyncClient as AC

    async with AC(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies={SESSION_COOKIE: cookie},
    ) as ac:
        resp = await ac.delete(f"/recipes/{recipe.id}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_recipe(auth_client: AsyncClient, session, user: User):
    recipe = Recipe(id=new_uuid7(), user_id=user.id, title="Old Title", slug="old-title-1", is_public=True)
    session.add(recipe)
    await session.commit()

    resp = await auth_client.patch(f"/recipes/{recipe.id}", json={"description": "Updated desc"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated desc"


@pytest.mark.asyncio
async def test_update_replaces_ingredients(auth_client: AsyncClient, session, user: User):
    recipe = Recipe(id=new_uuid7(), user_id=user.id, title="Ingredients Test", slug="ing-test-1", is_public=True)
    session.add(recipe)
    await session.commit()

    resp = await auth_client.patch(
        f"/recipes/{recipe.id}",
        json={"ingredients": [{"position": 1, "name": "salt"}]},
    )
    assert resp.status_code == 200
    assert len(resp.json()["ingredients"]) == 1
    assert resp.json()["ingredients"][0]["name"] == "salt"
