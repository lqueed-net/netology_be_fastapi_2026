"""Initial migration

Revision ID: 1fd390831342
Revises:
Create Date: 2026-05-21 14:01:33.323511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '1fd390831342'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_items_id', 'id')
    )

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_orders_id', 'id')
    )

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price_at_order', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_order_items_id', 'id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('items')
