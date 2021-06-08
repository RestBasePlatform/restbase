"""Add table size column

Revision ID: fd44d7dbabe1
Revises: 825baed58510
Create Date: 2021-04-26 08:10:01.138515

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "fd44d7dbabe1"
down_revision = "825baed58510"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tables_info", sa.Column("table_size", sa.INTEGER))

    op.add_column("tokens", sa.Column("main_admin", sa.BOOLEAN))


def downgrade():
    op.drop_column("tables_info", sa.Column("table_size", sa.INTEGER))

    op.drop_column("tokens", sa.Column("main_admin", sa.BOOLEAN))
