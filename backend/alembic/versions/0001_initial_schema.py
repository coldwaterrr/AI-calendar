"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-03-25 18:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial_schema'
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'events',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('tense', sa.String(length=16), nullable=False),
        sa.Column('category', sa.String(length=32), nullable=False),
        sa.Column('color', sa.String(length=16), nullable=False),
        sa.Column('source_type', sa.String(length=16), nullable=False, server_default='text'),
        sa.Column('raw_input', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'model_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('provider', sa.String(length=32), nullable=False),
        sa.Column('model', sa.String(length=128), nullable=False),
        sa.Column('base_url', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('encrypted_api_key', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('model_configs')
    op.drop_table('events')
