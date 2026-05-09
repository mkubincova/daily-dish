from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from app.utils.uuid7 import new_uuid7

if TYPE_CHECKING:
    from app.models.recipe import Recipe


def _now() -> datetime:
    return datetime.now(UTC)


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # pyright: ignore[reportAssignmentType]

    id: str = Field(primary_key=True)

    items: list["CategoryItem"] = Relationship(back_populates="category")


class CategoryItem(SQLModel, table=True):
    __tablename__ = "category_items"  # pyright: ignore[reportAssignmentType]

    id: str = Field(primary_key=True)
    category_id: str = Field(foreign_key="categories.id")

    category: "Category" = Relationship(back_populates="items")
    recipe_associations: list["RecipeCategoryItem"] = Relationship(back_populates="category_item")


class Tag(SQLModel, table=True):
    __tablename__ = "tags"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (sa.UniqueConstraint("name", name="tags_name_unique"),)

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    name: str
    created_by: str = Field(foreign_key="users.id")
    created_at: datetime = Field(
        default_factory=_now,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )

    recipe_associations: list["RecipeTag"] = Relationship(back_populates="tag")


class RecipeCategoryItem(SQLModel, table=True):
    __tablename__ = "recipe_category_items"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (sa.Index("recipe_category_items_category_item_idx", "category_item_id"),)

    recipe_id: str = Field(foreign_key="recipes.id", primary_key=True)
    category_item_id: str = Field(foreign_key="category_items.id", primary_key=True)

    recipe: "Recipe" = Relationship(back_populates="category_item_associations")
    category_item: CategoryItem = Relationship(back_populates="recipe_associations")


class RecipeTag(SQLModel, table=True):
    __tablename__ = "recipe_tags"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (sa.Index("recipe_tags_tag_idx", "tag_id"),)

    recipe_id: str = Field(foreign_key="recipes.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)

    recipe: "Recipe" = Relationship(back_populates="tag_associations")
    tag: Tag = Relationship(back_populates="recipe_associations")
