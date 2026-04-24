from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.utils.uuid7 import new_uuid7

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient
    from app.models.user import User


def _now() -> datetime:
    return datetime.now(UTC)


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"
    __table_args__ = (
        sa.UniqueConstraint("slug", name="recipes_slug_unique"),
        sa.Index("recipes_slug_idx", "slug"),
        sa.Index(
            "recipes_public_feed_idx",
            "created_at",
            postgresql_where=sa.text("is_public = true AND deleted_at IS NULL"),
        ),
        sa.Index(
            "recipes_owner_idx",
            "user_id",
            "created_at",
            postgresql_where=sa.text("deleted_at IS NULL"),
        ),
    )

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    image_public_id: str | None = None
    source_url: str | None = None
    servings: int | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    steps: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=sa.Column(
            sa.JSON().with_variant(JSONB(), "postgresql"),
            nullable=False,
            server_default="[]",
        ),
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
