from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.category import Category, CategoryItem

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryItemOut(BaseModel):
    id: str


class CategoryOut(BaseModel):
    id: str
    items: list[CategoryItemOut]


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[CategoryOut]:
    cats = list((await session.exec(select(Category))).all())
    items_result = list((await session.exec(select(CategoryItem))).all())

    items_by_cat: dict[str, list[CategoryItemOut]] = {}
    for item in items_result:
        items_by_cat.setdefault(item.category_id, []).append(CategoryItemOut(id=item.id))

    return [CategoryOut(id=cat.id, items=items_by_cat.get(cat.id, [])) for cat in cats]
