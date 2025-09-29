"""update column name

Revision ID: 51cfec6f622b
Revises: 4d932fd3bd66
Create Date: 2025-09-29 13:19:30.606832

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '51cfec6f622b'
down_revision: Union[str, Sequence[str], None] = '4d932fd3bd66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: rename column while preserving data."""
    op.alter_column(
        "historical_minute_trade_latencies",
        "total_trade_volume",
        new_column_name="total_trade_volume_in_quote"
    )


def downgrade() -> None:
    """Downgrade schema: revert the column rename."""
    op.alter_column(
        "historical_minute_trade_latencies",
        "total_trade_volume_in_quote",
        new_column_name="total_trade_volume"
    )
