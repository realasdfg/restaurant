"""menu_items price and cost non negative

Revision ID: 7b961fd9e871
Revises: 5a52003f67e5
Create Date: 2025-02-12 16:04:10.657273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b961fd9e871'
down_revision: Union[str, None] = '5a52003f67e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE menu_items ADD CONSTRAINT menu_items_check_price_non_negative CHECK (price >= 0)")
    op.execute("ALTER TABLE menu_items ADD CONSTRAINT menu_items_check_cost_non_negative CHECK (cost >= 0)")


def downgrade() -> None:
    op.execute("ALTER TABLE menu_items DROP CONSTRAINT menu_items_check_price_non_negative")
    op.execute("ALTER TABLE menu_items DROP CONSTRAINT menu_items_check_cost_non_negative")
