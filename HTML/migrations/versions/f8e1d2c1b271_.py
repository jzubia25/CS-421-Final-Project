"""empty message

Revision ID: f8e1d2c1b271
Revises: 83da635ce19b
Create Date: 2023-07-31 02:25:34.709691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8e1d2c1b271'
down_revision = '83da635ce19b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('pronouns', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('title', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('registrationDate', sa.DateTime(), nullable=True))
        batch_op.drop_column('firstName')
        batch_op.drop_column('lastName')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lastName', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('firstName', sa.TEXT(), nullable=True))
        batch_op.drop_column('registrationDate')
        batch_op.drop_column('title')
        batch_op.drop_column('pronouns')
        batch_op.drop_column('name')

    # ### end Alembic commands ###
