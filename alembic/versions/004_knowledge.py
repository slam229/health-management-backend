"""W4: Add knowledge and medical tables

Revision ID: 004
Revises: 003
Create Date: 2026-05-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # health_articles表
    op.create_table(
        'health_articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB, server_default='[]'),
        sa.Column('category', sa.String(64), nullable=True),
        sa.Column('source', sa.String(128), nullable=True),
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_health_articles_category', 'health_articles', ['category'])
    op.create_index('ix_health_articles_tags', 'health_articles', ['tags'], postgresql_using='gin')

    # medical_institutions表
    op.create_table(
        'medical_institutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('address', sa.String(512), nullable=True),
        sa.Column('longitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 7), nullable=True),
        sa.Column('department', sa.String(64), nullable=True),
        sa.Column('level', sa.String(32), nullable=True),
        sa.Column('phone', sa.String(32), nullable=True),
        sa.Column('website', sa.String(256), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_medical_institutions_department', 'medical_institutions', ['department'])
    op.create_index('ix_medical_institutions_level', 'medical_institutions', ['level'])


def downgrade() -> None:
    op.drop_table('medical_institutions')
    op.drop_table('health_articles')
