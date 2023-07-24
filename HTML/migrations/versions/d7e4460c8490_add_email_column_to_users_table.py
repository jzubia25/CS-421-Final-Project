"""Add email column to users table

Revision ID: d7e4460c8490
Revises: 
Create Date: 2023-07-24 12:06:20.673855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7e4460c8490'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('userName', sa.Text(), nullable=True))
        batch_op.drop_column('username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.TEXT(), nullable=True))
        batch_op.drop_column('userName')
        batch_op.drop_column('email')

    # ### end Alembic commands ###