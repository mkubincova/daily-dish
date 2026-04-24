from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from app.utils.uuid7 import new_uuid7

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient
    from app.models.user import User


def _now() -> datetime:
    return datetime.now(UTC)


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str
    slug: str = Field(unique=True, index=True)
    description: str | None = None
    image_url: str | None = None
    image_public_id: str | None = None
    source_url: str | None = None
    servings: int | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    steps: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=sa.Column(sa.JSON, nullable=False, server_default="[]"),
    )
    is_public: bool = Field(default=True)
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=_now,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_now,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )

    owner: "User" = Relationship(back_populates="recipes")
    ingredients: list["Ingredient"] = Relationship(back_populates="recipe")
