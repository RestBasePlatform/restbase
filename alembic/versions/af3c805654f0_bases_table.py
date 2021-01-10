"""bases_table

Revision ID: af3c805654f0
Revises: 38936c9e50e0
Create Date: 2021-01-01 20:02:32.814003

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "af3c805654f0"
down_revision = "38936c9e50e0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bases",
        sa.Column("id", sa.Integer),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("description", sa.String(200)),
        sa.Column("local_name", sa.String(200), nullable=False, primary_key=True),
        sa.Column("ip", sa.String(20), nullable=False),
        sa.Column("port", sa.String(4), nullable=False),
        sa.Column("database", sa.String(32), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password", sa.String(256), nullable=False),
    )


def downgrade():
    op.drop_table("bases")
