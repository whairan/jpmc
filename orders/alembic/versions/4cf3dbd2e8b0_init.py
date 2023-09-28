"""init

Revision ID: 4cf3dbd2e8b0
Revises: 032c8bc4e1fb
Create Date: 2023-09-28 00:24:18.269288

"""

# revision identifiers, used by Alembic.
revision = '4cf3dbd2e8b0'
down_revision = '032c8bc4e1fb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('order_details_product_id_idx', table_name='order_details')
    op.drop_index('orders_created_at_idx', table_name='orders')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('orders_created_at_idx', 'orders', ['created_at'], unique=False)
    op.create_index('order_details_product_id_idx', 'order_details', ['product_id'], unique=False)
    # ### end Alembic commands ###