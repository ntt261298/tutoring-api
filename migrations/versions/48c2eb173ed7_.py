"""empty message

Revision ID: 48c2eb173ed7
Revises: 922dc88dea20
Create Date: 2021-04-14 22:23:11.100925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48c2eb173ed7'
down_revision = '922dc88dea20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_subscription_package', sa.Column('status', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_subscription_package', 'status')
    # ### end Alembic commands ###
