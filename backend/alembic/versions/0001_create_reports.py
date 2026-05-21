"""create reports table

Revision ID: 0001_create_reports
Revises:
Create Date: 2026-05-11 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_create_reports"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("source_value", sa.Text(), nullable=False),
        sa.Column("recipe_title", sa.String(length=500), nullable=True),
        sa.Column("recipe_author", sa.String(length=255), nullable=True),
        sa.Column("cooking_time", sa.String(length=120), nullable=True),
        sa.Column("ingredients_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steps_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completeness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warnings_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("report_json", sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("reports")
