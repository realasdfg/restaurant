"""menu_items_check_weight_positive

Revision ID: d86f55acdb1a
Revises: 1cbd69af31fe
Create Date: 2025-02-14 03:54:35.782315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd86f55acdb1a'
down_revision: Union[str, None] = '1cbd69af31fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE menu_items ADD CONSTRAINT menu_items_check_weight_positive CHECK (weight >= 1)")


def downgrade() -> None:
    op.execute("ALTER TABLE menu_items DROP CONSTRAINT menu_items_check_weight_positive")
