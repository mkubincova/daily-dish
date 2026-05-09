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
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (
        sa.Index("users_email_idx", "email"),
        sa.UniqueConstraint("provider", "provider_id", name="users_provider_id_unique"),
    )

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    email: str
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
