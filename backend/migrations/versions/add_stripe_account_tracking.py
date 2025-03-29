"""add stripe account tracking

Revision ID: ae7fb892c123
Revises: fb5dae719aae
Create Date: 2023-08-12 18:30:45.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae7fb892c123'
down_revision = 'fb5dae719aae'  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns for tracking Stripe connected accounts
    try:
        # First try to add the dashboard_user_id column
        op.add_column('payments', sa.Column('dashboard_user_id', sa.Integer(), nullable=True))
    except Exception as e:
        print(f"Warning: Error adding dashboard_user_id column: {e}")
        
    try:
        # Then try to add the stripe_account_id column
        op.add_column('payments', sa.Column('stripe_account_id', sa.String(255), nullable=True))
    except Exception as e:
        print(f"Warning: Error adding stripe_account_id column: {e}")
    
    # Create indexes only if columns were added successfully
    try:
        op.create_index('idx_payments_dashboard_user', 'payments', ['dashboard_user_id'])
    except Exception as e:
        print(f"Warning: Error creating dashboard_user_id index: {e}")
        
    try:
        op.create_index('idx_payments_stripe_account', 'payments', ['stripe_account_id'])
    except Exception as e:
        print(f"Warning: Error creating stripe_account_id index: {e}")


def downgrade() -> None:
    # Remove the indexes first (with error handling)
    try:
        op.drop_index('idx_payments_stripe_account')
    except Exception as e:
        print(f"Warning: Error dropping stripe_account_id index: {e}")
        
    try:
        op.drop_index('idx_payments_dashboard_user')
    except Exception as e:
        print(f"Warning: Error dropping dashboard_user_id index: {e}")
    
    # Then remove the columns (with error handling)
    try:
        op.drop_column('payments', 'stripe_account_id')
    except Exception as e:
        print(f"Warning: Error dropping stripe_account_id column: {e}")
        
    try:
        op.drop_column('payments', 'dashboard_user_id')
    except Exception as e:
        print(f"Warning: Error dropping dashboard_user_id column: {e}") 