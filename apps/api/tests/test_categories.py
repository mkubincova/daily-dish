import pytest
from httpx import AsyncClient

from app.models.category import Category, CategoryItem


@pytest.mark.asyncio
async def test_list_categories_anonymous(client: AsyncClient, session):
    cat = Category(id="dish_type")
    item1 = CategoryItem(id="soup", category_id="dish_type")
    item2 = CategoryItem(id="salad", category_id="dish_type")
    session.add(cat)
    await session.flush()
    session.add(item1)
    session.add(item2)
    await session.commit()

    resp = await client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    cat_out = data[0]
    assert cat_out["id"] == "dish_type"
    item_ids = {i["id"] for i in cat_out["items"]}
    assert item_ids == {"soup", "salad"}


@pytest.mark.asyncio
async def test_categories_no_display_fields(client: AsyncClient, session):
    cat = Category(id="mood")
    item = CategoryItem(id="spicy", category_id="mood")
    session.add(cat)
    await session.flush()
    session.add(item)
    await session.commit()

    resp = await client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    for cat_out in data:
        assert "label" not in cat_out
        assert "position" not in cat_out
        assert "icon" not in cat_out
        assert "color" not in cat_out
        for item_out in cat_out["items"]:
            assert "label" not in item_out
            assert "position" not in item_out
            assert "icon" not in item_out
