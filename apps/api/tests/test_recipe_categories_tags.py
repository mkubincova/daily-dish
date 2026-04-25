"""Tests for recipe category/tag associations and list filters."""

import pytest
from httpx import AsyncClient

from app.models.category import Category, CategoryItem, Tag
from app.models.recipe import Recipe
from app.models.user import User
from app.utils.uuid7 import new_uuid7


async def _seed_taxonomy(session) -> None:
    cat = Category(id="dish_type")
    session.add(cat)
    await session.flush()
    for item_id in ["soup", "salad", "main"]:
        session.add(CategoryItem(id=item_id, category_id="dish_type"))
    cat2 = Category(id="mood")
    session.add(cat2)
    await session.flush()
    session.add(CategoryItem(id="vegetarian", category_id="mood"))
    await session.commit()


async def _seed_tag(session, name: str, user_id: str) -> Tag:
    tag = Tag(id=new_uuid7(), name=name, created_by=user_id)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@pytest.mark.asyncio
async def test_create_recipe_with_categories_and_tags(
    auth_client: AsyncClient, session, user: User
):
    await _seed_taxonomy(session)
    tag = await _seed_tag(session, "christmas", user.id)

    resp = await auth_client.post(
        "/recipes",
        json={
            "title": "Soup Recipe",
            "is_public": True,
            "category_item_ids": ["soup"],
            "tag_ids": [tag.id],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["category_items"] == [{"id": "soup", "category_id": "dish_type"}]
    assert data["tags"] == [{"id": tag.id, "name": "christmas"}]


@pytest.mark.asyncio
async def test_create_recipe_unknown_category_item_rejected(
    auth_client: AsyncClient, session, user: User
):
    await _seed_taxonomy(session)
    resp = await auth_client.post(
        "/recipes",
        json={"title": "Bad Cat", "category_item_ids": ["nonexistent"]},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_recipe_unknown_tag_rejected(auth_client: AsyncClient, session, user: User):
    resp = await auth_client.post(
        "/recipes",
        json={"title": "Bad Tag", "tag_ids": ["00000000-0000-0000-0000-000000000000"]},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_replaces_associations(auth_client: AsyncClient, session, user: User):
    await _seed_taxonomy(session)
    tag1 = await _seed_tag(session, "weeknight", user.id)
    tag2 = await _seed_tag(session, "easy", user.id)

    r = await auth_client.post(
        "/recipes",
        json={
            "title": "Salad",
            "category_item_ids": ["salad"],
            "tag_ids": [tag1.id],
        },
    )
    assert r.status_code == 201
    recipe_id = r.json()["id"]

    r2 = await auth_client.patch(
        f"/recipes/{recipe_id}",
        json={"category_item_ids": ["main"], "tag_ids": [tag2.id]},
    )
    assert r2.status_code == 200
    data = r2.json()
    assert [c["id"] for c in data["category_items"]] == ["main"]
    assert [t["id"] for t in data["tags"]] == [tag2.id]


@pytest.mark.asyncio
async def test_soft_delete_leaves_associations(auth_client: AsyncClient, session, user: User):
    from sqlmodel import select

    from app.models.category import RecipeCategoryItem

    await _seed_taxonomy(session)
    r = await auth_client.post(
        "/recipes",
        json={"title": "To Delete", "category_item_ids": ["soup"]},
    )
    assert r.status_code == 201
    recipe_id = r.json()["id"]

    del_resp = await auth_client.delete(f"/recipes/{recipe_id}")
    assert del_resp.status_code == 204

    result = await session.exec(
        select(RecipeCategoryItem).where(RecipeCategoryItem.recipe_id == recipe_id)
    )
    assert len(result.all()) == 1


@pytest.mark.asyncio
async def test_list_filter_single_category(client: AsyncClient, session, user: User):
    await _seed_taxonomy(session)
    soup_r = Recipe(id=new_uuid7(), user_id=user.id, title="Soup", slug="soup-1", is_public=True)
    salad_r = Recipe(id=new_uuid7(), user_id=user.id, title="Salad", slug="salad-1", is_public=True)
    session.add(soup_r)
    session.add(salad_r)
    await session.flush()
    from app.models.category import RecipeCategoryItem

    session.add(RecipeCategoryItem(recipe_id=soup_r.id, category_item_id="soup"))
    session.add(RecipeCategoryItem(recipe_id=salad_r.id, category_item_id="salad"))
    await session.commit()

    resp = await client.get("/recipes?category_items=soup")
    assert resp.status_code == 200
    slugs = [r["slug"] for r in resp.json()["items"]]
    assert "soup-1" in slugs
    assert "salad-1" not in slugs


@pytest.mark.asyncio
async def test_list_filter_or_within_group(client: AsyncClient, session, user: User):
    await _seed_taxonomy(session)
    soup_r = Recipe(id=new_uuid7(), user_id=user.id, title="Soup", slug="soup-2", is_public=True)
    salad_r = Recipe(id=new_uuid7(), user_id=user.id, title="Salad", slug="salad-2", is_public=True)
    main_r = Recipe(id=new_uuid7(), user_id=user.id, title="Main", slug="main-2", is_public=True)
    for r in [soup_r, salad_r, main_r]:
        session.add(r)
    await session.flush()
    from app.models.category import RecipeCategoryItem

    session.add(RecipeCategoryItem(recipe_id=soup_r.id, category_item_id="soup"))
    session.add(RecipeCategoryItem(recipe_id=salad_r.id, category_item_id="salad"))
    session.add(RecipeCategoryItem(recipe_id=main_r.id, category_item_id="main"))
    await session.commit()

    resp = await client.get("/recipes?category_items=soup,salad")
    assert resp.status_code == 200
    slugs = {r["slug"] for r in resp.json()["items"]}
    assert "soup-2" in slugs
    assert "salad-2" in slugs
    assert "main-2" not in slugs


@pytest.mark.asyncio
async def test_list_filter_and_across_groups(client: AsyncClient, session, user: User):
    await _seed_taxonomy(session)
    both = Recipe(
        id=new_uuid7(), user_id=user.id, title="Veg Soup", slug="veg-soup-3", is_public=True
    )
    only_soup = Recipe(
        id=new_uuid7(), user_id=user.id, title="Soup only", slug="soup-only-3", is_public=True
    )
    for r in [both, only_soup]:
        session.add(r)
    await session.flush()
    from app.models.category import RecipeCategoryItem

    session.add(RecipeCategoryItem(recipe_id=both.id, category_item_id="soup"))
    session.add(RecipeCategoryItem(recipe_id=both.id, category_item_id="vegetarian"))
    session.add(RecipeCategoryItem(recipe_id=only_soup.id, category_item_id="soup"))
    await session.commit()

    resp = await client.get("/recipes?category_items=soup&category_items=vegetarian")
    assert resp.status_code == 200
    slugs = {r["slug"] for r in resp.json()["items"]}
    assert "veg-soup-3" in slugs
    assert "soup-only-3" not in slugs


@pytest.mark.asyncio
async def test_list_filter_unknown_id_returns_empty(client: AsyncClient, session, user: User):
    recipe = Recipe(id=new_uuid7(), user_id=user.id, title="Any", slug="any-4", is_public=True)
    session.add(recipe)
    await session.commit()

    resp = await client.get("/recipes?category_items=nonexistent_id")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


@pytest.mark.asyncio
async def test_mine_status_filter_published(auth_client: AsyncClient, session, user: User):
    pub = Recipe(id=new_uuid7(), user_id=user.id, title="Pub", slug="pub-s1", is_public=True)
    draft = Recipe(id=new_uuid7(), user_id=user.id, title="Draft", slug="draft-s1", is_public=False)
    session.add(pub)
    session.add(draft)
    await session.commit()

    resp = await auth_client.get("/recipes/mine?status=published")
    assert resp.status_code == 200
    slugs = {r["slug"] for r in resp.json()}
    assert "pub-s1" in slugs
    assert "draft-s1" not in slugs


@pytest.mark.asyncio
async def test_mine_status_filter_draft(auth_client: AsyncClient, session, user: User):
    pub = Recipe(id=new_uuid7(), user_id=user.id, title="Pub", slug="pub-s2", is_public=True)
    draft = Recipe(id=new_uuid7(), user_id=user.id, title="Draft", slug="draft-s2", is_public=False)
    session.add(pub)
    session.add(draft)
    await session.commit()

    resp = await auth_client.get("/recipes/mine?status=draft")
    assert resp.status_code == 200
    slugs = {r["slug"] for r in resp.json()}
    assert "draft-s2" in slugs
    assert "pub-s2" not in slugs


@pytest.mark.asyncio
async def test_mine_status_combined_with_category(auth_client: AsyncClient, session, user: User):
    await _seed_taxonomy(session)
    draft_main = Recipe(
        id=new_uuid7(), user_id=user.id, title="Draft Main", slug="draft-main-s3", is_public=False
    )
    draft_soup = Recipe(
        id=new_uuid7(), user_id=user.id, title="Draft Soup", slug="draft-soup-s3", is_public=False
    )
    session.add(draft_main)
    session.add(draft_soup)
    await session.flush()
    from app.models.category import RecipeCategoryItem

    session.add(RecipeCategoryItem(recipe_id=draft_main.id, category_item_id="main"))
    session.add(RecipeCategoryItem(recipe_id=draft_soup.id, category_item_id="soup"))
    await session.commit()

    resp = await auth_client.get("/recipes/mine?status=draft&category_items=main")
    assert resp.status_code == 200
    slugs = {r["slug"] for r in resp.json()}
    assert "draft-main-s3" in slugs
    assert "draft-soup-s3" not in slugs
