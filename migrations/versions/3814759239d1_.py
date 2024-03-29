"""empty message

Revision ID: 3814759239d1
Revises: 187fd612acab
Create Date: 2021-05-05 20:41:19.301632

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3814759239d1'
down_revision = '187fd612acab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('file_id', sa.Integer(), nullable=True))
    op.drop_column('question', 'file_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('file_url', mysql.VARCHAR(length=1024), nullable=True))
    op.drop_column('question', 'file_id')
    # ### end Alembic commands ###
