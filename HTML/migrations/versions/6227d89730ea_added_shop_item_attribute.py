"""Added shop_item attribute

Revision ID: 6227d89730ea
Revises: 5d8fb7cc0c72
Create Date: 2023-08-02 22:31:27.338446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6227d89730ea'
down_revision = '5d8fb7cc0c72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artworks', sa.Column('shop_item', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artworks', 'shop_item')
    # ### end Alembic commands ###
