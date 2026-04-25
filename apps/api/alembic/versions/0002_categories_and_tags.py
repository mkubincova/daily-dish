"""categories and tags

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "category_items",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_by", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="tags_name_unique"),
    )
    op.create_table(
        "recipe_category_items",
        sa.Column("recipe_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category_item_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.ForeignKeyConstraint(["category_item_id"], ["category_items.id"]),
        sa.PrimaryKeyConstraint("recipe_id", "category_item_id"),
    )
    op.create_index(
        "recipe_category_items_category_item_idx",
        "recipe_category_items",
        ["category_item_id"],
    )
    op.create_table(
        "recipe_tags",
        sa.Column("recipe_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tag_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"]),
        sa.PrimaryKeyConstraint("recipe_id", "tag_id"),
    )
    op.create_index("recipe_tags_tag_idx", "recipe_tags", ["tag_id"])

    # Seed v1 taxonomy
    op.bulk_insert(
        sa.table("categories", sa.column("id", sa.String)),
        [{"id": "dish_type"}, {"id": "mood"}, {"id": "protein"}],
    )
    op.bulk_insert(
        sa.table(
            "category_items",
            sa.column("id", sa.String),
            sa.column("category_id", sa.String),
        ),
        [
            {"id": "soup", "category_id": "dish_type"},
            {"id": "salad", "category_id": "dish_type"},
            {"id": "main", "category_id": "dish_type"},
            {"id": "side", "category_id": "dish_type"},
            {"id": "dessert", "category_id": "dish_type"},
            {"id": "snack", "category_id": "dish_type"},
            {"id": "light", "category_id": "mood"},
            {"id": "vegetarian", "category_id": "mood"},
            {"id": "spicy", "category_id": "mood"},
            {"id": "hearty", "category_id": "mood"},
            {"id": "fried", "category_id": "mood"},
            {"id": "beef", "category_id": "protein"},
            {"id": "chicken", "category_id": "protein"},
            {"id": "pork", "category_id": "protein"},
            {"id": "fish", "category_id": "protein"},
            {"id": "rabbit", "category_id": "protein"},
            {"id": "duck", "category_id": "protein"},
            {"id": "turkey", "category_id": "protein"},
            {"id": "plant_based", "category_id": "protein"},
        ],
    )


def downgrade() -> None:
    op.drop_index("recipe_tags_tag_idx", table_name="recipe_tags")
    op.drop_table("recipe_tags")
    op.drop_index(
        "recipe_category_items_category_item_idx",
        table_name="recipe_category_items",
    )
    op.drop_table("recipe_category_items")
    op.drop_table("tags")
    op.drop_table("category_items")
    op.drop_table("categories")
