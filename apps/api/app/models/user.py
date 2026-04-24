from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from app.utils.uuid7 import new_uuid7

if TYPE_CHECKING:
    from app.models.recipe import Recipe


def _now() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    email: str = Field(index=True)
    name: str
    avatar_url: str | None = None
    provider: str
    provider_id: str
    created_at: datetime = Field(
        default_factory=_now,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_now,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )

    recipes: list["Recipe"] = Relationship(back_populates="owner")
