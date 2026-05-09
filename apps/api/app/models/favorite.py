from datetime import UTC, datetime

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from app.utils.uuid7 import new_uuid7


def _now() -> datetime:
    return datetime.now(UTC)


class UserFavorite(SQLModel, table=True):
    __tablename__ = "user_favorites"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (
        sa.UniqueConstraint("user_id", "recipe_id", name="user_favorites_unique"),
        sa.Index("user_favorites_user_idx", "user_id"),
    )

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    recipe_id: str = Field(foreign_key="recipes.id")
    created_at: datetime = Field(
        default_factory=_now,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
