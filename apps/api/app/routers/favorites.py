from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.deps import get_current_user
from app.models.favorite import UserFavorite
from app.models.recipe import Recipe
from app.models.user import User
from app.routers.recipes import (
    PAGE_SIZE,
    OwnerPublic,
    PaginatedRecipes,
    RecipeListItem,
    _batch_load_associations,
    _filter_clauses,
)

router = APIRouter(tags=["favorites"])


@router.get("/users/me/favorites", response_model=PaginatedRecipes)
async def list_favorites(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=PAGE_SIZE, ge=1, le=100),
    category_items: list[str] = Query(default=[]),
    tags: list[str] = Query(default=[]),
) -> PaginatedRecipes:
    base_conditions = [
        UserFavorite.user_id == current_user.id,
        Recipe.deleted_at.is_(None),  # type: ignore[union-attr]
        *_filter_clauses(category_items, tags),
    ]

    count_stmt = (
        select(Recipe)
        .join(UserFavorite, UserFavorite.recipe_id == Recipe.id)
        .where(*base_conditions)
    )
    count_result = await session.exec(count_stmt)
    total = len(count_result.all())

    stmt = (
        select(Recipe)
        .join(UserFavorite, UserFavorite.recipe_id == Recipe.id)
        .where(*base_conditions)
        .order_by(UserFavorite.created_at.desc())  # type: ignore[union-attr]
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.exec(stmt)
    recipes = list(result.all())

    recipe_ids = [r.id for r in recipes]
    cat_map, tag_map = await _batch_load_associations(session, recipe_ids)

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
                is_favorited=True,
            )
        )

    return PaginatedRecipes(items=items, total=total, page=page, page_size=page_size)
