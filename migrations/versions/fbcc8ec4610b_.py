"""empty message

Revision ID: fbcc8ec4610b
Revises: 3209251ff9fc
Create Date: 2021-04-21 17:04:25.196229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbcc8ec4610b'
down_revision = '3209251ff9fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('expert', sa.Column('status', sa.String(length=64), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('expert', 'status')
    # ### end Alembic commands ###