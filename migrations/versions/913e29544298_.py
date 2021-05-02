"""empty message

Revision ID: 913e29544298
Revises: fbcc8ec4610b
Create Date: 2021-04-26 21:58:41.397086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '913e29544298'
down_revision = 'fbcc8ec4610b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('status', sa.String(length=64), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    # ### end Alembic commands ###