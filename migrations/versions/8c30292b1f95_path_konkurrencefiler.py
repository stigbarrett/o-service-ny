"""Path konkurrencefiler

Revision ID: 8c30292b1f95
Revises: 904ad08900a1
Create Date: 2022-06-08 11:25:01.356783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c30292b1f95'
down_revision = '904ad08900a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('baner', sa.Column('path_filer', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('baner', 'path_filer')
    # ### end Alembic commands ###
