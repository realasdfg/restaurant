"""strings min length constraint

Revision ID: 5a52003f67e5
Revises: 8e554c113d41
Create Date: 2025-02-12 00:10:45.726630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a52003f67e5'
down_revision: Union[str, None] = '8e554c113d41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD CONSTRAINT users_check_username_length CHECK (LENGTH(username) >= 3)")
    op.execute("ALTER TABLE users ADD CONSTRAINT users_check_first_name_length CHECK (LENGTH(first_name) >= 1)")
    op.execute("ALTER TABLE users ADD CONSTRAINT users_check_last_name_length CHECK (LENGTH(last_name) >= 1)")
    op.execute("ALTER TABLE tables ADD CONSTRAINT tables_check_name_length CHECK (LENGTH(name) >= 1)")
    op.execute("ALTER TABLE menu_categories ADD CONSTRAINT menu_categories_check_name_length CHECK (LENGTH(name) >= 1)")
    op.execute("ALTER TABLE menu_items ADD CONSTRAINT menu_items_check_name_length CHECK (LENGTH(name) >= 1)")


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT check_username_length")
    op.execute("ALTER TABLE users DROP CONSTRAINT check_first_name_length")
    op.execute("ALTER TABLE users DROP CONSTRAINT check_last_name_length")
    op.execute("ALTER TABLE tables DROP CONSTRAINT tables_check_name_length")
    op.execute("ALTER TABLE menu_categories DROP CONSTRAINT menu_categories_check_name_length")
    op.execute("ALTER TABLE menu_items DROP CONSTRAINT menu_items_check_name_length")
