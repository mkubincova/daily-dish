from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import delete
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.deps import get_current_user, get_current_user_optional
from app.models.category import CategoryItem, RecipeCategoryItem, RecipeTag, Tag
from app.models.favorite import UserFavorite
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.user import User
from app.utils.slug import slugify
from app.utils.uuid7 import new_uuid7

router = APIRouter(prefix="/recipes", tags=["recipes"])

PAGE_SIZE = 20


class IngredientIn(BaseModel):
    position: int
    quantity: Decimal | None = None
    unit: str | None = None
    name: str
    notes: str | None = None


class RecipeIn(BaseModel):
    title: str
    description: str | None = None
    image_url: str | None = None
    image_public_id: str | None = None
    source_url: str | None = None
    servings: int | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    steps: list[dict[str, Any]] = []
    is_public: bool = True
    ingredients: list[IngredientIn] = []
    category_item_ids: list[str] = []
    tag_ids: list[str] = []


class RecipePatch(BaseModel):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    image_public_id: str | None = None
    source_url: str | None = None
    servings: int | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    steps: list[dict[str, Any]] | None = None
    is_public: bool | None = None
    ingredients: list[IngredientIn] | None = None
    category_item_ids: list[str] | None = None
    tag_ids: list[str] | None = None


class OwnerPublic(BaseModel):
    name: str
    avatar_url: str | None


class IngredientOut(BaseModel):
    id: str
    position: int
    quantity: Decimal | None
    unit: str | None
    name: str
    notes: str | None


class CategoryItemOut(BaseModel):
    id: str
    category_id: str


class TagOut(BaseModel):
    id: str
    name: str


class RecipeOut(BaseModel):
    id: str
    user_id: str
    slug: str
    title: str
    description: str | None
    image_url: str | None
    image_public_id: str | None
    source_url: str | None
    servings: int | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    steps: list[dict[str, Any]]
    is_public: bool
    created_at: datetime
    updated_at: datetime
    owner: OwnerPublic
    ingredients: list[IngredientOut]
    category_items: list[CategoryItemOut]
    tags: list[TagOut]
    is_favorited: bool | None = None


class RecipeListItem(BaseModel):
    id: str
    slug: str
    title: str
    description: str | None
    image_url: str | None
    is_public: bool
    created_at: datetime
    owner: OwnerPublic
    category_item_ids: list[str]
    tag_ids: list[str]
    is_favorited: bool | None = None


class PaginatedRecipes(BaseModel):
    items: list[RecipeListItem]
    total: int
    page: int
    page_size: int


class FavoriteOut(BaseModel):
    is_favorited: bool


class TrashedRecipeItem(BaseModel):
    id: str
    slug: str
    title: str
    image_url: str | None
    deleted_at: datetime


def _recipe_out(
    recipe: Recipe,
    owner: User,
    ingredients: list[Ingredient],
    category_assocs: list[RecipeCategoryItem],
    tag_assocs: list[tuple[RecipeTag, Tag]],
    is_favorited: bool | None = None,
) -> RecipeOut:
    return RecipeOut(
        id=recipe.id,
        user_id=recipe.user_id,
        slug=recipe.slug,
        title=recipe.title,
        description=recipe.description,
        image_url=recipe.image_url,
        image_public_id=recipe.image_public_id,
        source_url=recipe.source_url,
        servings=recipe.servings,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        steps=recipe.steps or [],
        is_public=recipe.is_public,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        owner=OwnerPublic(name=owner.name, avatar_url=owner.avatar_url),
        ingredients=[
            IngredientOut(
                id=i.id,
                position=i.position,
                quantity=i.quantity,
                unit=i.unit,
                name=i.name,
                notes=i.notes,
            )
            for i in sorted(ingredients, key=lambda x: x.position)
        ],
        category_items=[
            CategoryItemOut(id=a.category_item_id, category_id=_item_category(a))
            for a in category_assocs
        ],
        tags=[TagOut(id=rt.tag_id, name=tag.name) for rt, tag in tag_assocs],
        is_favorited=is_favorited,
    )


def _item_category(assoc: RecipeCategoryItem) -> str:
    # category_item_id is a text PK; we need the category_id from the join
    # The CategoryItem is eagerly available via assoc.category_item when loaded
    return assoc.category_item.category_id if assoc.category_item else ""


async def _load_ingredients(session: AsyncSession, recipe_id: str) -> list[Ingredient]:
    result = await session.exec(
        select(Ingredient)
        .where(col(Ingredient.recipe_id) == recipe_id)
        .order_by(col(Ingredient.position))
    )
    return list(result.all())


async def _load_category_assocs(session: AsyncSession, recipe_id: str) -> list[RecipeCategoryItem]:
    result = await session.exec(
        select(RecipeCategoryItem, CategoryItem)
        .join(CategoryItem, col(RecipeCategoryItem.category_item_id) == col(CategoryItem.id))
        .where(col(RecipeCategoryItem.recipe_id) == recipe_id)
    )
    rows = result.all()
    # Attach category_item onto assoc for later use in _item_category
    assocs = []
    for assoc, item in rows:
        assoc.category_item = item
        assocs.append(assoc)
    return assocs


async def _load_tag_assocs(session: AsyncSession, recipe_id: str) -> list[tuple[RecipeTag, Tag]]:
    result = await session.exec(
        select(RecipeTag, Tag)
        .join(Tag, col(RecipeTag.tag_id) == col(Tag.id))
        .where(col(RecipeTag.recipe_id) == recipe_id)
    )
    return list(result.all())


async def _replace_ingredients(
    session: AsyncSession, recipe_id: str, ingredients: list[IngredientIn]
) -> None:
    await session.exec(delete(Ingredient).where(Ingredient.recipe_id == recipe_id))  # type: ignore[arg-type]
    for ing in ingredients:
        session.add(
            Ingredient(
                id=new_uuid7(),
                recipe_id=recipe_id,
                position=ing.position,
                quantity=ing.quantity,
                unit=ing.unit,
                name=ing.name,
                notes=ing.notes,
            )
        )


async def _validate_and_replace_associations(
    session: AsyncSession,
    recipe_id: str,
    category_item_ids: list[str],
    tag_ids: list[str],
) -> None:
    if category_item_ids:
        found = list(
            (
                await session.exec(
                    select(CategoryItem).where(CategoryItem.id.in_(category_item_ids))  # type: ignore[attr-defined]
                )
            ).all()
        )
        found_ids = {item.id for item in found}
        missing = set(category_item_ids) - found_ids
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown category_item_ids: {sorted(missing)}",
            )

    if tag_ids:
        found_tags = list(
            (
                await session.exec(select(Tag).where(Tag.id.in_(tag_ids)))  # type: ignore[attr-defined]
            ).all()
        )
        found_tag_ids = {t.id for t in found_tags}
        missing_tags = set(tag_ids) - found_tag_ids
        if missing_tags:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown tag_ids: {sorted(missing_tags)}",
            )

    await session.exec(  # type: ignore[arg-type]
        delete(RecipeCategoryItem).where(col(RecipeCategoryItem.recipe_id) == recipe_id)
    )
    await session.exec(  # type: ignore[arg-type]
        delete(RecipeTag).where(col(RecipeTag.recipe_id) == recipe_id)
    )
    for item_id in category_item_ids:
        session.add(RecipeCategoryItem(recipe_id=recipe_id, category_item_id=item_id))
    for tag_id in tag_ids:
        session.add(RecipeTag(recipe_id=recipe_id, tag_id=tag_id))


@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    body: RecipeIn,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeOut:
    slug = slugify(body.title)
    recipe = Recipe(
        id=new_uuid7(),
        user_id=current_user.id,
        title=body.title,
        slug=slug,
        description=body.description,
        image_url=body.image_url,
        image_public_id=body.image_public_id,
        source_url=body.source_url,
        servings=body.servings,
        prep_time_minutes=body.prep_time_minutes,
        cook_time_minutes=body.cook_time_minutes,
        steps=body.steps,
        is_public=body.is_public,
    )
    session.add(recipe)
    await session.flush()
    await _replace_ingredients(session, recipe.id, body.ingredients)
    await _validate_and_replace_associations(
        session, recipe.id, body.category_item_ids, body.tag_ids
    )
    await session.commit()
    await session.refresh(recipe)
    ingredients = await _load_ingredients(session, recipe.id)
    category_assocs = await _load_category_assocs(session, recipe.id)
    tag_assocs = await _load_tag_assocs(session, recipe.id)
    return _recipe_out(recipe, current_user, ingredients, category_assocs, tag_assocs)


@router.patch("/{recipe_id}", response_model=RecipeOut)
async def update_recipe(
    recipe_id: str,
    body: RecipePatch,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeOut:
    stmt = select(Recipe).where(
        Recipe.id == recipe_id,
        Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
        Recipe.user_id == current_user.id,
    )
    result = await session.exec(stmt)
    recipe = result.first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not found")

    old_image_public_id = recipe.image_public_id

    update_data = body.model_dump(exclude_unset=True)
    ingredients_data = update_data.pop("ingredients", None)
    category_item_ids = update_data.pop("category_item_ids", None)
    tag_ids = update_data.pop("tag_ids", None)
    for key, val in update_data.items():
        setattr(recipe, key, val)
    recipe.updated_at = datetime.now(UTC)
    session.add(recipe)

    if ingredients_data is not None:
        parsed = [IngredientIn(**i) for i in ingredients_data]
        await _replace_ingredients(session, recipe.id, parsed)

    if category_item_ids is not None or tag_ids is not None:
        await _validate_and_replace_associations(
            session,
            recipe.id,
            category_item_ids or [],
            tag_ids or [],
        )

    await session.commit()

    new_image_public_id = update_data.get("image_public_id")
    if old_image_public_id and new_image_public_id and new_image_public_id != old_image_public_id:
        from app.routers.uploads import _destroy_cloudinary_image

        await _destroy_cloudinary_image(old_image_public_id)

    await session.refresh(recipe)
    owner = await session.get(User, recipe.user_id)
    ingredients = await _load_ingredients(session, recipe.id)
    category_assocs = await _load_category_assocs(session, recipe.id)
    tag_assocs = await _load_tag_assocs(session, recipe.id)
    return _recipe_out(recipe, owner, ingredients, category_assocs, tag_assocs)  # type: ignore[arg-type]


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    stmt = select(Recipe).where(
        Recipe.id == recipe_id,
        Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
        Recipe.user_id == current_user.id,
    )
    result = await session.exec(stmt)
    recipe = result.first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not found")
    recipe.deleted_at = datetime.now(UTC)
    session.add(recipe)
    await session.commit()


async def _batch_load_associations(
    session: AsyncSession, recipe_ids: list[str]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    if not recipe_ids:
        return {}, {}
    cat_result = await session.exec(
        select(RecipeCategoryItem).where(RecipeCategoryItem.recipe_id.in_(recipe_ids))  # type: ignore[attr-defined]
    )
    tag_result = await session.exec(
        select(RecipeTag).where(RecipeTag.recipe_id.in_(recipe_ids))  # type: ignore[attr-defined]
    )
    cat_map: dict[str, list[str]] = {}
    for a in cat_result.all():
        cat_map.setdefault(a.recipe_id, []).append(a.category_item_id)
    tag_map: dict[str, list[str]] = {}
    for a in tag_result.all():
        tag_map.setdefault(a.recipe_id, []).append(a.tag_id)
    return cat_map, tag_map


async def _batch_load_favorites(
    session: AsyncSession, user_id: str, recipe_ids: list[str]
) -> set[str]:
    if not recipe_ids:
        return set()
    result = await session.exec(
        select(UserFavorite.recipe_id).where(  # type: ignore[attr-defined]
            UserFavorite.user_id == user_id,
            UserFavorite.recipe_id.in_(recipe_ids),  # type: ignore[attr-defined]
        )
    )
    return set(result.all())


def _filter_clauses(
    category_item_params: list[str],
    tag_params: list[str],
) -> list:
    """Build EXISTS clauses: OR within param value, AND across param occurrences."""
    import sqlalchemy as sa

    clauses = []
    for raw in category_item_params:
        group = [v.strip() for v in raw.split(",") if v.strip()]
        if group:
            clauses.append(
                sa.exists(
                    select(RecipeCategoryItem.recipe_id).where(
                        RecipeCategoryItem.recipe_id == Recipe.id,
                        RecipeCategoryItem.category_item_id.in_(group),  # type: ignore[attr-defined]
                    )
                )
            )
    for raw in tag_params:
        group = [v.strip() for v in raw.split(",") if v.strip()]
        if group:
            clauses.append(
                sa.exists(
                    select(RecipeTag.recipe_id).where(
                        RecipeTag.recipe_id == Recipe.id,
                        RecipeTag.tag_id.in_(group),  # type: ignore[attr-defined]
                    )
                )
            )
    return clauses


@router.post("/{recipe_id}/favorite", response_model=FavoriteOut)
async def add_favorite(
    recipe_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FavoriteOut:
    result = await session.exec(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.deleted_at.is_(None))  # type: ignore[union-attr]
    )
    if result.first() is None:
        raise HTTPException(status_code=404, detail="Not found")

    existing = await session.exec(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.recipe_id == recipe_id,
        )
    )
    if existing.first() is None:
        session.add(UserFavorite(user_id=current_user.id, recipe_id=recipe_id))
        await session.commit()
    return FavoriteOut(is_favorited=True)


@router.delete("/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    recipe_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await session.exec(  # type: ignore[arg-type]
        delete(UserFavorite).where(
            col(UserFavorite.user_id) == current_user.id,
            col(UserFavorite.recipe_id) == recipe_id,
        )
    )
    await session.commit()


@router.post("/{recipe_id}/restore", response_model=RecipeOut)
async def restore_recipe(
    recipe_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeOut:
    result = await session.exec(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not found")
    if recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if recipe.deleted_at is None:
        raise HTTPException(status_code=409, detail="Recipe is not deleted")
    recipe.deleted_at = None
    recipe.updated_at = datetime.now(UTC)
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    owner = await session.get(User, recipe.user_id)
    ingredients = await _load_ingredients(session, recipe.id)
    category_assocs = await _load_category_assocs(session, recipe.id)
    tag_assocs = await _load_tag_assocs(session, recipe.id)
    return _recipe_out(recipe, owner, ingredients, category_assocs, tag_assocs)  # type: ignore[arg-type]


@router.delete("/{recipe_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanently_delete_recipe(
    recipe_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await session.exec(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not found")
    if recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if recipe.deleted_at is None:
        raise HTTPException(status_code=409, detail="Recipe is not in trash")
    image_public_id = recipe.image_public_id
    await session.exec(delete(Ingredient).where(Ingredient.recipe_id == recipe_id))  # type: ignore[arg-type]
    await session.exec(delete(RecipeCategoryItem).where(RecipeCategoryItem.recipe_id == recipe_id))  # type: ignore[arg-type]
    await session.exec(delete(RecipeTag).where(RecipeTag.recipe_id == recipe_id))  # type: ignore[arg-type]
    await session.exec(delete(UserFavorite).where(UserFavorite.recipe_id == recipe_id))  # type: ignore[arg-type]
    await session.exec(delete(Recipe).where(Recipe.id == recipe_id))  # type: ignore[arg-type]
    await session.commit()
    if image_public_id:
        from app.routers.uploads import _destroy_cloudinary_image

        await _destroy_cloudinary_image(image_public_id)


@router.get("/mine", response_model=list[RecipeListItem])
async def list_mine(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    category_items: list[str] = Query(default=[]),
    tags: list[str] = Query(default=[]),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[RecipeListItem]:
    conditions = [
        Recipe.user_id == current_user.id,
        Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
    ]
    if status_filter == "published":
        conditions.append(Recipe.is_public == True)  # noqa: E712
    elif status_filter == "draft":
        conditions.append(Recipe.is_public == False)  # noqa: E712

    conditions.extend(_filter_clauses(category_items, tags))

    stmt = select(Recipe).where(*conditions).order_by(Recipe.created_at.desc())  # type: ignore[union-attr]
    result = await session.exec(stmt)
    recipes = list(result.all())

    recipe_ids = [r.id for r in recipes]
    cat_map, tag_map = await _batch_load_associations(session, recipe_ids)
    fav_set = await _batch_load_favorites(session, current_user.id, recipe_ids)

    owner = OwnerPublic(name=current_user.name, avatar_url=current_user.avatar_url)
    return [
        RecipeListItem(
            id=r.id,
            slug=r.slug,
            title=r.title,
            description=r.description,
            image_url=r.image_url,
            is_public=r.is_public,
            created_at=r.created_at,
            owner=owner,
            category_item_ids=cat_map.get(r.id, []),
            tag_ids=tag_map.get(r.id, []),
            is_favorited=r.id in fav_set,
        )
        for r in recipes
    ]


@router.get("", response_model=PaginatedRecipes)
async def list_recipes(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=PAGE_SIZE, ge=1, le=100),
    category_items: list[str] = Query(default=[]),
    tags: list[str] = Query(default=[]),
) -> PaginatedRecipes:
    # Filter change resets pagination: clients should pass page=1 when filters change.
    base_conditions = [
        Recipe.is_public == True,  # noqa: E712
        Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
        *_filter_clauses(category_items, tags),
    ]
    count_result = await session.exec(select(Recipe).where(*base_conditions))
    total = len(count_result.all())

    stmt = (
        select(Recipe)
        .where(*base_conditions)
        .order_by(Recipe.created_at.desc())  # type: ignore[union-attr]
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.exec(stmt)
    recipes = list(result.all())

    recipe_ids = [r.id for r in recipes]
    cat_map, tag_map = await _batch_load_associations(session, recipe_ids)
    fav_set = (
        await _batch_load_favorites(session, current_user.id, recipe_ids) if current_user else set()
    )

    items = []
    for r in recipes:
        owner = await session.get(User, r.user_id)
        items.append(
            RecipeListItem(
                id=r.id,
                slug=r.slug,
                title=r.title,
                description=r.description,
                image_url=r.image_url,
                is_public=r.is_public,
                created_at=r.created_at,
                owner=OwnerPublic(
                    name=owner.name if owner else "",
                    avatar_url=owner.avatar_url if owner else None,
                ),
                category_item_ids=cat_map.get(r.id, []),
                tag_ids=tag_map.get(r.id, []),
                is_favorited=r.id in fav_set if current_user else None,
            )
        )

    return PaginatedRecipes(items=items, total=total, page=page, page_size=page_size)


@router.get("/trashed", response_model=list[TrashedRecipeItem])
async def list_trashed(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TrashedRecipeItem]:
    stmt = (
        select(Recipe)
        .where(
            Recipe.user_id == current_user.id,
            Recipe.deleted_at.is_not(None),  # type: ignore[union-attr]
        )
        .order_by(Recipe.deleted_at.desc())  # type: ignore[union-attr]
    )
    result = await session.exec(stmt)
    recipes = list(result.all())
    return [
        TrashedRecipeItem(
            id=r.id,
            slug=r.slug,
            title=r.title,
            image_url=r.image_url,
            deleted_at=r.deleted_at,  # type: ignore[arg-type]
        )
        for r in recipes
    ]


@router.get("/{slug}", response_model=RecipeOut)
async def get_recipe(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
) -> RecipeOut:
    stmt = select(Recipe).where(Recipe.slug == slug, Recipe.deleted_at.is_(None))  # type: ignore[union-attr]
    result = await session.exec(stmt)
    recipe = result.first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not found")

    if not recipe.is_public and (current_user is None or current_user.id != recipe.user_id):
        raise HTTPException(status_code=404, detail="Not found")

    owner = await session.get(User, recipe.user_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Not found")
    ingredients = await _load_ingredients(session, recipe.id)
    category_assocs = await _load_category_assocs(session, recipe.id)
    tag_assocs = await _load_tag_assocs(session, recipe.id)

    is_favorited: bool | None = None
    if current_user:
        fav = await session.exec(
            select(UserFavorite).where(
                UserFavorite.user_id == current_user.id,
                UserFavorite.recipe_id == recipe.id,
            )
        )
        is_favorited = fav.first() is not None

    return _recipe_out(recipe, owner, ingredients, category_assocs, tag_assocs, is_favorited)
