"""make clinic inactive by default

Revision ID: 0e07c75dd861
Revises: 04b8aca01c94
Create Date: 2025-12-19 07:17:59.400374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e07c75dd861'
down_revision: Union[str, Sequence[str], None] = '04b8aca01c94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'clinics'
        ) THEN
            ALTER TABLE clinics
            ALTER COLUMN is_active SET DEFAULT false;
        END IF;
    END$$;
    """)


def downgrade():
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'clinics'
        ) THEN
            ALTER TABLE clinics
            ALTER COLUMN is_active SET DEFAULT true;
        END IF;
    END$$;
    """)
