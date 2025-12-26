"""add created_at to report_images

Revision ID: d7ccd58a4862
Revises: da3a297f1ac6
Create Date: 2025-12-26 06:31:32.105077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7ccd58a4862'
down_revision: Union[str, Sequence[str], None] = 'da3a297f1ac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - ONLY add created_at column to report_images."""
    # Add the created_at column to report_images table
    op.add_column('report_images',
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    """Downgrade schema - remove created_at column from report_images."""
    # Remove the created_at column from report_images table
    op.drop_column('report_images', 'created_at')