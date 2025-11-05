"""Add Google OAuth fields to User model

Revision ID: google_oauth_001
Revises: 7d80be6f0f6c
Create Date: 2025-10-14 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'google_oauth_001'
down_revision = '7d80be6f0f6c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add Google OAuth fields to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_id', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('auth_provider', sa.String(50), nullable=False, server_default='email'))
        batch_op.create_index('ix_users_google_id', ['google_id'], unique=True)

def downgrade() -> None:
    # Remove Google OAuth fields from users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_google_id')
        batch_op.drop_column('auth_provider')
        batch_op.drop_column('google_id')