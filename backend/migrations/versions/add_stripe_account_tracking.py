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
    op.add_column('payments', sa.Column('dashboard_user_id', sa.Integer(), nullable=True))
    op.add_column('payments', sa.Column('stripe_account_id', sa.String(255), nullable=True))
    
    # Add indexes for performance
    op.create_index('idx_payments_dashboard_user', 'payments', ['dashboard_user_id'])
    op.create_index('idx_payments_stripe_account', 'payments', ['stripe_account_id'])


def downgrade() -> None:
    # Remove the indexes first
    op.drop_index('idx_payments_stripe_account')
    op.drop_index('idx_payments_dashboard_user')
    
    # Then remove the columns
    op.drop_column('payments', 'stripe_account_id')
    op.drop_column('payments', 'dashboard_user_id') 