"""added timezone column foin user table

Revision ID: 7469b7303850
Revises: 2e9802842506
Create Date: 2022-12-15 20:51:22.980495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7469b7303850'
down_revision = '2e9802842506'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timezone', sa.String(length=30), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('timezone')

    # ### end Alembic commands ###
