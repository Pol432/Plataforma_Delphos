"""add_immersive_fields
Revision ID: e5f6a7d8c9ab
Revises: b47178168b0e
Create Date: 2026-08-15 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e5f6a7d8c9ab'
down_revision = 'b47178168b0e'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to simulations
    op.add_column('simulations', sa.Column('lore_context', sa.Text(), nullable=True))
    op.add_column('simulations', sa.Column('scaffolding_phase', sa.String(length=50), nullable=False, server_default='Guided'))
    op.add_column('simulations', sa.Column('real_world_constraints', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('simulations', sa.Column('immediate_feedback', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column('simulations', sa.Column('skills_metrics_weights', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))

    # Add columns to module_tasks
    op.add_column('module_tasks', sa.Column('lore_context', sa.Text(), nullable=True))
    op.add_column('module_tasks', sa.Column('scaffolding_phase', sa.String(length=50), nullable=False, server_default='Guided'))
    op.add_column('module_tasks', sa.Column('real_world_constraints', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('module_tasks', sa.Column('immediate_feedback', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column('module_tasks', sa.Column('skills_metrics_weights', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))


def downgrade():
    # Drop columns from module_tasks
    op.drop_column('module_tasks', 'skills_metrics_weights')
    op.drop_column('module_tasks', 'immediate_feedback')
    op.drop_column('module_tasks', 'real_world_constraints')
    op.drop_column('module_tasks', 'scaffolding_phase')
    op.drop_column('module_tasks', 'lore_context')

    # Drop columns from simulations
    op.drop_column('simulations', 'skills_metrics_weights')
    op.drop_column('simulations', 'immediate_feedback')
    op.drop_column('simulations', 'real_world_constraints')
    op.drop_column('simulations', 'scaffolding_phase')
    op.drop_column('simulations', 'lore_context')
