"""menu item available default true

Revision ID: e2f8d74a6842
Revises: 6a9dd3dc3d11
Create Date: 2024-11-08 23:11:35.198955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f8d74a6842'
down_revision: Union[str, None] = '6a9dd3dc3d11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('menu_items', 'available',
                    server_default=sa.text('TRUE'),)


def downgrade() -> None:
    op.alter_column('menu_items', 'available',
                    server_default=None, )
