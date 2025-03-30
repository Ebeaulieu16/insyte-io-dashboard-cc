"""add_funnel_table

Revision ID: 12bd2cced072
Revises: 322a806f7904
Create Date: 2025-03-30 05:35:15.888661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12bd2cced072'
down_revision = '322a806f7904'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the funnel table
    op.create_table('funnels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('link_clicks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('calls_booked', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('calls_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('deals_closed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_revenue', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_type', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['slug'], ['video_links.slug'], name=op.f('fk_funnels_slug_video_links'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_funnels'))
    )
    
    # Create indexes
    op.create_index(op.f('idx_funnel_slug'), 'funnels', ['slug'], unique=False)
    op.create_index(op.f('idx_funnel_user_id'), 'funnels', ['user_id'], unique=False)
    op.create_index(op.f('idx_funnel_period'), 'funnels', ['period_type', 'period_start', 'period_end'], unique=False)
    op.create_index(op.f('idx_funnel_slug_user'), 'funnels', ['slug', 'user_id'], unique=False)


def downgrade() -> None:
    # Drop the funnel table
    op.drop_index(op.f('idx_funnel_slug_user'), table_name='funnels')
    op.drop_index(op.f('idx_funnel_period'), table_name='funnels')
    op.drop_index(op.f('idx_funnel_user_id'), table_name='funnels')
    op.drop_index(op.f('idx_funnel_slug'), table_name='funnels')
    op.drop_table('funnels') 