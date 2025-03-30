"""update_call_status_enum

Revision ID: 322a806f7904
Revises: 91a36b4dbacb
Create Date: 2025-03-30 05:21:15.967209

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '322a806f7904'
down_revision = '91a36b4dbacb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if the enum type exists
    conn = op.get_bind()
    result = conn.execute(text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'callstatus');"))
    type_exists = result.scalar()
    
    if type_exists:
        # If the type exists, rename and update it
        op.execute(text("ALTER TYPE callstatus RENAME TO callstatus_old;"))
        op.execute(text("CREATE TYPE callstatus AS ENUM ('booked', 'pending', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled');"))
        
        # Update the column to use the new enum type
        # First convert to text to avoid type validation
        op.execute(text("ALTER TABLE calls ALTER COLUMN status TYPE TEXT;"))
        
        # Convert existing values to match new enum values
        # Map 'live' to 'confirmed' (closest match)
        op.execute(text("UPDATE calls SET status = 'confirmed' WHERE status = 'live';"))
        
        # Now convert back to the new enum type
        op.execute(text("ALTER TABLE calls ALTER COLUMN status TYPE callstatus USING status::callstatus;"))
        
        # Drop the old enum type
        op.execute(text("DROP TYPE callstatus_old;"))
    else:
        # If the type doesn't exist, create it new
        op.execute(text("CREATE TYPE callstatus AS ENUM ('booked', 'pending', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled');"))
        
        # Create a new column with the enum type
        op.execute(text("ALTER TABLE calls ALTER COLUMN status TYPE callstatus USING status::callstatus;"))


def downgrade() -> None:
    # Check if the enum type exists
    conn = op.get_bind()
    result = conn.execute(text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'callstatus');"))
    type_exists = result.scalar()
    
    if not type_exists:
        # If the type doesn't exist, nothing to do
        return
    
    # Create a temporary enum type with the old values
    op.execute(text("ALTER TYPE callstatus RENAME TO callstatus_new;"))
    op.execute(text("CREATE TYPE callstatus AS ENUM ('booked', 'live', 'no_show', 'rescheduled');"))
    
    # Update the column to use the old enum type
    # First convert to text to avoid type validation
    op.execute(text("ALTER TABLE calls ALTER COLUMN status TYPE TEXT;"))
    
    # Convert new values back to old enum values
    op.execute(text("UPDATE calls SET status = 'live' WHERE status IN ('confirmed', 'completed');"))
    op.execute(text("UPDATE calls SET status = 'booked' WHERE status IN ('pending', 'cancelled');"))
    
    # Now convert back to the old enum type
    op.execute(text("ALTER TABLE calls ALTER COLUMN status TYPE callstatus USING status::callstatus;"))
    
    # Drop the new enum type
    op.execute(text("DROP TYPE callstatus_new;")) 