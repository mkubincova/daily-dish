from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from app.utils.uuid7 import new_uuid7

if TYPE_CHECKING:
    from app.models.recipe import Recipe


class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"
    __table_args__ = (sa.Index("ingredients_recipe_pos_idx", "recipe_id", "position"),)

    id: str = Field(default_factory=new_uuid7, primary_key=True)
    recipe_id: str = Field(foreign_key="recipes.id")
    position: int
    quantity: Decimal | None = None
    unit: str | None = None
    name: str
    notes: str | None = None

    recipe: "Recipe" = Relationship(back_populates="ingredients")
