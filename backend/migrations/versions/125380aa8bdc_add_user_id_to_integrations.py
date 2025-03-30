"""add_user_id_to_integrations

Revision ID: 125380aa8bdc
Revises: 12bd2cced072
Create Date: 2025-03-30 11:43:37.665887

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '125380aa8bdc'
down_revision = '12bd2cced072'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update the existing user_id column values to 1
    op.execute("UPDATE integrations SET user_id = 1 WHERE user_id IS NULL")


def downgrade() -> None:
    # No downgrade needed
    pass 