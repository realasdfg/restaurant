"""add category name max length

Revision ID: 6a9dd3dc3d11
Revises: 36c70cf3e68e
Create Date: 2024-11-08 21:48:34.062299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a9dd3dc3d11'
down_revision: Union[str, None] = '36c70cf3e68e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('menu_categories', 'name',
                    existing_type=sa.String(),
                    type_=sa.String(length=50))


def downgrade() -> None:
    op.alter_column('menu_categories', 'name',
                    existing_type=sa.String(length=50),
                    type_=sa.String())
