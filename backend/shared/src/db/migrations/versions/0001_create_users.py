"""create users table

Revision ID: 0001_create_users
Revises: None
Create Date: 2025-09-24
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa

from shared.src.models.base import GUID

# revision identifiers, used by Alembic.
revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow),
    )


def downgrade() -> None:
    op.drop_table("users")
