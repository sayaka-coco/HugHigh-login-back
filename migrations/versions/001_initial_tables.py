"""Initial tables: users and auth_logs

Revision ID: 001
Revises:
Create Date: 2025-12-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # usersテーブル作成
    op.create_table(
        'users',
        sa.Column('id', mysql.CHAR(32), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('role', sa.Integer(), nullable=False),
        sa.Column('google_sub', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('student_id', sa.String(50), nullable=True),
        sa.Column('class_name', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_sub')
    )
    op.create_index('idx_email', 'users', ['email'])
    op.create_index('idx_role', 'users', ['role'])

    # auth_logsテーブル作成
    op.create_table(
        'auth_logs',
        sa.Column('id', mysql.CHAR(32), nullable=False),
        sa.Column('user_id', mysql.CHAR(32), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_id', 'auth_logs', ['user_id'])
    op.create_index('idx_timestamp', 'auth_logs', ['timestamp'])
    op.create_index('idx_event_type', 'auth_logs', ['event_type'])


def downgrade() -> None:
    op.drop_index('idx_event_type', 'auth_logs')
    op.drop_index('idx_timestamp', 'auth_logs')
    op.drop_index('idx_user_id', 'auth_logs')
    op.drop_table('auth_logs')

    op.drop_index('idx_role', 'users')
    op.drop_index('idx_email', 'users')
    op.drop_table('users')
