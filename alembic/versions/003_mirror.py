"""W1/W3: Add mirror_tasks table

Revision ID: 003
Revises: 002
Create Date: 2026-05-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mirror_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('face_image_url', sa.String(512), nullable=True),
        sa.Column('bad_habits', postgresql.JSONB, server_default='[]'),
        sa.Column('target_years', sa.Integer(), server_default='5'),
        sa.Column('status', sa.String(16), server_default='pending'),
        sa.Column('progress', sa.Integer(), server_default='0'),
        sa.Column('progress_msg', sa.String(256), nullable=True),
        sa.Column('result_image_url', sa.String(512), nullable=True),
        sa.Column('medical_warning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_mirror_tasks_user_id', 'mirror_tasks', ['user_id'])
    op.create_index('ix_mirror_tasks_status', 'mirror_tasks', ['status'])


def downgrade() -> None:
    op.drop_table('mirror_tasks')
