"""add_user_id_to_integrations

Revision ID: 125380aa8bdc
Revises: 12bd2cced072
Create Date: 2025-03-30 11:43:37.665887

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.exc

# revision identifiers, used by Alembic.
revision = '125380aa8bdc'
down_revision = '12bd2cced072'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Try to update the user_id column, which will fail if it doesn't exist
    try:
        op.execute("UPDATE integrations SET user_id = 1 WHERE user_id IS NULL")
        print("user_id column exists, updated NULL values to 1")
    except sqlalchemy.exc.ProgrammingError as e:
        if 'column "user_id" of relation "integrations" does not exist' in str(e):
            # Column doesn't exist, so add it
            print("user_id column doesn't exist, adding it now")
            op.execute("ALTER TABLE integrations ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
            op.execute("CREATE INDEX idx_integration_user_id ON integrations (user_id)")
            op.execute("CREATE INDEX idx_integration_user_platform ON integrations (user_id, platform)")
            print("Added user_id column and indexes")
        else:
            # Some other error occurred
            raise e


def downgrade() -> None:
    # We won't provide a downgrade path for this migration
    pass 