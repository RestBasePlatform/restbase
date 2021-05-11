"""test_table_1

Revision ID: 41a89aff45aa
Revises:
Create Date: 2021-01-06 10:21:00.618815

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "41a89aff45aa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "test_table_1",
        sa.Column("int_column", sa.Integer),
        sa.Column("bool_column", sa.Boolean),
        sa.Column("text_columns", sa.Text),
    )


def downgrade():
    op.drop_table("test_table_1")
