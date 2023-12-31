"""init

Revision ID: a0a6a7b7a2d2
Revises: 68e6cff61e79
Create Date: 2023-09-27 23:45:53.472525

"""

# revision identifiers, used by Alembic.
revision = 'a0a6a7b7a2d2'
down_revision = '68e6cff61e79'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('order_details_product_id_idx', 'order_details', ['product_id'], unique=False)
    op.create_index('orders_created_at_idx', 'orders', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('orders_created_at_idx', table_name='orders')
    op.drop_index('order_details_product_id_idx', table_name='order_details')
    # ### end Alembic commands ###
