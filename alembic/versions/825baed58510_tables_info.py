"""tables_info

Revision ID: 825baed58510
Revises: af3c805654f0
Create Date: 2021-01-01 20:57:59.375871

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = "825baed58510"
down_revision = "af3c805654f0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tables_info",
        sa.Column("table_name", sa.String(64), nullable=False),
        sa.Column(
            "folder_name", sa.String(64), nullable=False
        ),  # something like schema
        sa.Column("database_name", sa.String(), sa.ForeignKey("bases.name")),
        sa.Column("local_name", sa.String(200), nullable=False, primary_key=True),
        sa.Column("columns", postgresql.JSON(), nullable=False),
    )


def downgrade():
    op.drop_table("tables_info")
