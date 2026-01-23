"""add_dividends_and_stock_splits_to_stock_prices

Revision ID: 557bcf16f26d
Revises: 1c153ee17b84
Create Date: 2026-01-23 18:53:05.569907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '557bcf16f26d'
down_revision: Union[str, Sequence[str], None] = '1c153ee17b84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('stock_prices', sa.Column('dividends', sa.DECIMAL(10, 4), nullable=True, server_default='0'))
    op.add_column('stock_prices', sa.Column('stock_splits', sa.DECIMAL(10, 4), nullable=True, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('stock_prices', 'stock_splits')
    op.drop_column('stock_prices', 'dividends')
