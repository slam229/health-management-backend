"""W1: Add risk_assessments, health_plans, plan_executions tables

Revision ID: 002
Revises: 001
Create Date: 2026-05-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # risk_assessments表
    op.create_table(
        'risk_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('risk_level', sa.String(16), nullable=False),
        sa.Column('risk_score', sa.Numeric(4, 2), nullable=True),
        sa.Column('detail', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_risk_assessments_user_id', 'risk_assessments', ['user_id'])

    # health_plans表
    op.create_table(
        'health_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan_type', sa.String(16), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_health_plans_user_id', 'health_plans', ['user_id'])

    # plan_executions表
    op.create_table(
        'plan_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('health_plans.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('item_type', sa.String(16), nullable=False),
        sa.Column('item_index', sa.Integer(), nullable=False),
        sa.Column('completed', sa.Boolean(), server_default='false'),
        sa.Column('checkin_date', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_plan_executions_user_id', 'plan_executions', ['user_id'])
    op.create_index('ix_plan_executions_plan_id', 'plan_executions', ['plan_id'])


def downgrade() -> None:
    op.drop_table('plan_executions')
    op.drop_table('health_plans')
    op.drop_table('risk_assessments')
