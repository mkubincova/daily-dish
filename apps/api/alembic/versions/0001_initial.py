"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-24

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_id", name="users_provider_id_unique"),
    )
    op.create_index("users_email_idx", "users", ["email"])

    op.create_table(
        "recipes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("image_public_id", sa.String(), nullable=True),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("cook_time_minutes", sa.Integer(), nullable=True),
        sa.Column("steps", JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="recipes_slug_unique"),
    )
    # Partial index: public feed (is_public=true, deleted_at IS NULL), ordered by created_at
    op.create_index(
        "recipes_public_feed_idx",
        "recipes",
        ["created_at"],
        postgresql_where=sa.text("is_public = true AND deleted_at IS NULL"),
    )
    # Partial index: owner's recipes (deleted_at IS NULL)
    op.create_index(
        "recipes_owner_idx",
        "recipes",
        ["user_id", "created_at"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    # Index on slug for fast lookup
    op.create_index("recipes_slug_idx", "recipes", ["slug"])

    op.create_table(
        "ingredients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("recipe_id", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    # Index: ingredients ordered by recipe + position
    op.create_index(
        "ingredients_recipe_pos_idx",
        "ingredients",
        ["recipe_id", "position"],
    )


def downgrade() -> None:
    op.drop_index("ingredients_recipe_pos_idx", table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_index("recipes_slug_idx", table_name="recipes")
    op.drop_index("recipes_owner_idx", table_name="recipes")
    op.drop_index("recipes_public_feed_idx", table_name="recipes")
    op.drop_table("recipes")
    op.drop_index("users_email_idx", table_name="users")
    op.drop_table("users")
