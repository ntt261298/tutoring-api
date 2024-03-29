"""empty message

Revision ID: 187fd612acab
Revises: dd09c5162d2e
Create Date: 2021-05-05 11:27:07.007407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '187fd612acab'
down_revision = 'dd09c5162d2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_rating', sa.Column('topic_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_rating', 'topic', ['topic_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_rating', type_='foreignkey')
    op.drop_column('user_rating', 'topic_id')
    # ### end Alembic commands ###
