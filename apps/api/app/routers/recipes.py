from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import delete
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.deps import get_current_user, get_current_user_optional
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


class RecipeListItem(BaseModel):
    id: str
    slug: str
    title: str
    description: str | None
    image_url: str | None
    is_public: bool
    created_at: datetime
    owner: OwnerPublic


class PaginatedRecipes(BaseModel):
    items: list[RecipeListItem]
    total: int
    page: int
    page_size: int


def _recipe_out(recipe: Recipe, owner: User, ingredients: list[Ingredient]) -> RecipeOut:
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
    )


async def _load_ingredients(session: AsyncSession, recipe_id: str) -> list[Ingredient]:
    result = await session.exec(
        select(Ingredient).where(Ingredient.recipe_id == recipe_id).order_by(Ingredient.position)
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
    await session.commit()
    await session.refresh(recipe)
    ingredients = await _load_ingredients(session, recipe.id)
    return _recipe_out(recipe, current_user, ingredients)


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

    update_data = body.model_dump(exclude_unset=True)
    ingredients_data = update_data.pop("ingredients", None)
    for key, val in update_data.items():
        setattr(recipe, key, val)
    recipe.updated_at = datetime.now(UTC)
    session.add(recipe)

    if ingredients_data is not None:
        parsed = [IngredientIn(**i) for i in ingredients_data]
        await _replace_ingredients(session, recipe.id, parsed)

    await session.commit()
    await session.refresh(recipe)
    owner = await session.get(User, recipe.user_id)
    ingredients = await _load_ingredients(session, recipe.id)
    return _recipe_out(recipe, owner, ingredients)  # type: ignore[arg-type]


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


@router.get("/mine", response_model=list[RecipeListItem])
async def list_mine(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[RecipeListItem]:
    stmt = (
        select(Recipe)
        .where(
            Recipe.user_id == current_user.id,
            Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
        )
        .order_by(Recipe.created_at.desc())  # type: ignore[union-attr]
    )
    result = await session.exec(stmt)
    recipes = result.all()
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
        )
        for r in recipes
    ]


@router.get("", response_model=PaginatedRecipes)
async def list_recipes(
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=PAGE_SIZE, ge=1, le=100),
) -> PaginatedRecipes:
    base = and_(
        Recipe.is_public == True,  # noqa: E712
        Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
    )
    count_result = await session.exec(select(Recipe).where(base))
    total = len(count_result.all())

    stmt = (
        select(Recipe)
        .where(base)
        .order_by(Recipe.created_at.desc())  # type: ignore[union-attr]
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.exec(stmt)
    recipes = result.all()

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
            )
        )

    return PaginatedRecipes(items=items, total=total, page=page, page_size=page_size)


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
    return _recipe_out(recipe, owner, ingredients)
