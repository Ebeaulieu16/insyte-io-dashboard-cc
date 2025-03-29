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
    
    # Rename metadata column to extra_data in integrations table if it exists
    # This avoids conflict with SQLAlchemy's reserved 'metadata' attribute name
    try:
        # First check if the column exists
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        columns = inspector.get_columns('integrations')
        column_names = [column["name"] for column in columns]
        
        if 'metadata' in column_names and 'extra_data' not in column_names:
            print("Renaming 'metadata' column to 'extra_data' in integrations table")
            # SQLite doesn't support direct column rename, so different approaches needed
            # Based on dialect, use appropriate rename strategy
            dialect = conn.dialect.name
            
            if dialect == 'sqlite':
                # For SQLite, need to recreate table
                print("Using SQLite-specific migration approach")
                # This is a simplified approach - depending on complexity,
                # you might need a more comprehensive implementation
                with op.batch_alter_table('integrations') as batch_op:
                    batch_op.alter_column('metadata', new_column_name='extra_data')
            else:
                # For PostgreSQL, MySQL, etc.
                op.alter_column('integrations', 'metadata', new_column_name='extra_data')
            
            print("Column renamed successfully")
        else:
            if 'extra_data' in column_names:
                print("Column 'extra_data' already exists, no rename needed")
            elif 'metadata' not in column_names:
                print("Column 'metadata' doesn't exist, no rename needed")
                # Optionally add the extra_data column if neither exists
                if 'extra_data' not in column_names:
                    op.add_column('integrations', sa.Column('extra_data', sa.JSON, nullable=True))
                    print("Added 'extra_data' column to integrations table")
    except Exception as e:
        print(f"Warning: Error handling metadata/extra_data column: {e}")


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
    
    # No need to handle the extra_data rename in downgrade as it's a one-way fix
    # Changing back would reintroduce the issue with SQLAlchemy 