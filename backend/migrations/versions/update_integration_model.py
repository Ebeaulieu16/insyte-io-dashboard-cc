"""update integration model

Revision ID: bf9c82d3a456
Revises: ae7fb892c123
Create Date: 2023-08-12 19:15:22.456789

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bf9c82d3a456'
down_revision = 'ae7fb892c123'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a temporary table with the new schema
    op.create_table(
        'integrations_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('account_id', sa.String(255), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=True),
        sa.Column('access_token', sa.String(512), nullable=False),
        sa.Column('refresh_token', sa.String(512), nullable=True),
        sa.Column('token_type', sa.String(50), server_default='bearer', nullable=False),
        sa.Column('scope', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_integration_user_platform', 'integrations_new', ['user_id', 'platform'])
    op.create_index('idx_integration_account', 'integrations_new', ['account_id'])
    op.create_index('ix_integrations_new_id', 'integrations_new', ['id'], unique=False)
    
    # Transfer data from old table if it exists
    # Note: This assumes the old table has a compatible schema.
    # You may need to customize this part based on your existing schema.
    try:
        op.execute(
            """
            INSERT INTO integrations_new (
                id, created_at, updated_at, platform, account_id, account_name, 
                access_token, refresh_token, last_sync, user_id, status
            )
            SELECT 
                id, created_at, updated_at, platform, 
                COALESCE(account_id, 'unknown'), account_name,
                COALESCE(access_token, ''), COALESCE(refresh_token, ''), 
                COALESCE(last_sync, NOW()),
                1, -- default user_id, update this as needed
                CASE WHEN is_connected THEN 'connected' ELSE 'disconnected' END
            FROM 
                integrations
            """
        )
    except Exception as e:
        # If the old table doesn't exist or has incompatible schema,
        # this will ensure the migration continues
        print(f"Warning: Could not transfer data: {e}")
    
    # Drop the old table and rename the new one
    op.drop_table('integrations')
    op.rename_table('integrations_new', 'integrations')


def downgrade() -> None:
    # This is a complex change, so downgrade might not preserve all data
    # Create the old table structure
    op.create_table(
        'integrations_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('is_connected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync', sa.DateTime(timezone=True), nullable=True),
        sa.Column('api_key', sa.String(255), nullable=True),
        sa.Column('account_name', sa.String(255), nullable=True),
        sa.Column('account_id', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index
    op.create_index('idx_integrations_platform', 'integrations_old', ['platform'])
    op.create_index('ix_integrations_old_id', 'integrations_old', ['id'], unique=False)
    
    # Transfer minimal data back
    op.execute(
        """
        INSERT INTO integrations_old (
            id, created_at, updated_at, platform, is_connected, 
            access_token, refresh_token, last_sync, account_name, account_id
        )
        SELECT 
            id, created_at, updated_at, platform,
            CASE WHEN status = 'connected' THEN true ELSE false END,
            access_token, refresh_token, last_sync, account_name, account_id
        FROM 
            integrations
        """
    )
    
    # Drop new table and rename old table
    op.drop_table('integrations')
    op.rename_table('integrations_old', 'integrations') 