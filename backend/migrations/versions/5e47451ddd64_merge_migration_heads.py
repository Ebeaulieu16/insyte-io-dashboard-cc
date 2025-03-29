"""merge_migration_heads

Revision ID: 5e47451ddd64
Revises: 21c8e5320101, bf9c82d3a456
Create Date: 2025-03-29 01:43:15.159895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e47451ddd64'
down_revision = ('21c8e5320101', 'bf9c82d3a456')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 