"""token_table

Revision ID: 38936c9e50e0
Revises:
Create Date: 2021-01-01 19:37:49.675792

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = "38936c9e50e0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tokens",
        sa.Column("token", sa.String(64), nullable=False, primary_key=True),
        sa.Column("description", sa.String(200)),
        sa.Column("granted_tables", postgresql.ARRAY(postgresql.TEXT, dimensions=1)),
        sa.Column("admin_access", sa.Boolean()),
    )


def downgrade():
    op.drop_table("tokens")
