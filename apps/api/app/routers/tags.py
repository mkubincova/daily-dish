from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, field_validator
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.deps import get_current_user
from app.models.category import Tag
from app.models.user import User
from app.utils.uuid7 import new_uuid7

router = APIRouter(prefix="/tags", tags=["tags"])


def _normalize(name: str) -> str:
    return " ".join(name.strip().lower().split())


class TagIn(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v


class TagOut(BaseModel):
    id: str
    name: str


@router.get("", response_model=list[TagOut])
async def list_tags(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TagOut]:
    result = await session.exec(select(Tag).order_by(Tag.name))
    return [TagOut(id=t.id, name=t.name) for t in result.all()]


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(
    body: TagIn,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TagOut:
    normalised = _normalize(body.name)
    if not normalised:
        raise HTTPException(status_code=422, detail="name must not be empty after normalisation")

    existing = (await session.exec(select(Tag).where(Tag.name == normalised))).first()
    if existing:
        response.status_code = status.HTTP_200_OK
        return TagOut(id=existing.id, name=existing.name)

    tag = Tag(id=new_uuid7(), name=normalised, created_by=current_user.id)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return TagOut(id=tag.id, name=tag.name)
