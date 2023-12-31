"""empty message

Revision ID: 0d14636ce3dd
Revises: 5d8fb7cc0c72
Create Date: 2023-08-02 21:08:42.028921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d14636ce3dd'
down_revision = '5d8fb7cc0c72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_pic', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('author_id', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('author_id')
        batch_op.drop_column('profile_pic')

    # ### end Alembic commands ###
