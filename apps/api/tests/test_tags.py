import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_list_tags_anonymous(client: AsyncClient, session, user: User):
    resp = await client.get("/api/tags")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_tag_requires_auth(client: AsyncClient):
    resp = await client.post("/api/tags", json={"name": "spicy"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_tag_normalises_name(auth_client: AsyncClient):
    resp = await auth_client.post("/api/tags", json={"name": "  Spicy   Dish "})
    assert resp.status_code == 201
    assert resp.json()["name"] == "spicy dish"


@pytest.mark.asyncio
async def test_create_tag_lowercase(auth_client: AsyncClient):
    resp = await auth_client.post("/api/tags", json={"name": "HEARTY"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "hearty"


@pytest.mark.asyncio
async def test_create_tag_idempotent(auth_client: AsyncClient):
    r1 = await auth_client.post("/api/tags", json={"name": "christmas"})
    assert r1.status_code == 201
    r2 = await auth_client.post("/api/tags", json={"name": "Christmas"})
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


@pytest.mark.asyncio
async def test_create_tag_empty_name_rejected(auth_client: AsyncClient):
    resp = await auth_client.post("/api/tags", json={"name": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_tags_ordered_alphabetically(auth_client: AsyncClient):
    await auth_client.post("/api/tags", json={"name": "zucchini"})
    await auth_client.post("/api/tags", json={"name": "apple"})
    await auth_client.post("/api/tags", json={"name": "mango"})

    resp = await auth_client.get("/api/tags")
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()]
    assert names == sorted(names)
