"""initial

Revision ID: 4785974c345f
Revises:
Create Date: 2021-08-25 19:13:20.944027

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "4785974c345f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "installed_modules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("module_name", sa.String(), nullable=True),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column("installation_date", sa.DateTime(), nullable=True),
        sa.Column("functions_config", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "secrets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("secret", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("secrets")
    op.drop_table("installed_modules")
    # ### end Alembic commands ###