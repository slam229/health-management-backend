"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-05-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('username', sa.String(64), unique=True, nullable=False),
        sa.Column('email', sa.String(128), unique=True, nullable=True),
        sa.Column('password_hash', sa.String(256), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # health_profiles表
    op.create_table(
        'health_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('gender', sa.String(8), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('height_cm', sa.Numeric(5, 1), nullable=True),
        sa.Column('weight_kg', sa.Numeric(5, 1), nullable=True),
        sa.Column('chronic_diseases', postgresql.JSONB, server_default='[]'),
        sa.Column('family_history', postgresql.JSONB, server_default='[]'),
        sa.Column('allergies', postgresql.JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )

    # health_records表
    op.create_table(
        'health_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('source', sa.String(32), nullable=False),
        sa.Column('metrics', postgresql.JSONB, nullable=False),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_health_records_user_id', 'health_records', ['user_id'])
    op.create_index('ix_health_records_recorded_at', 'health_records', ['recorded_at'])

    # anomaly_alerts表
    op.create_table(
        'anomaly_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('alert_type', sa.String(32), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('metric_name', sa.String(32), nullable=False),
        sa.Column('metric_value', sa.String(32), nullable=False),
        sa.Column('threshold_value', sa.String(32), nullable=False),
        sa.Column('title', sa.String(128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_anomaly_alerts_user_id', 'anomaly_alerts', ['user_id'])
    op.create_index('ix_anomaly_alerts_created_at', 'anomaly_alerts', ['created_at'])


def downgrade() -> None:
    op.drop_table('anomaly_alerts')
    op.drop_table('health_records')
    op.drop_table('health_profiles')
    op.drop_table('users')
