"""add_careers_to_users

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7d8c9ab
Create Date: 2026-08-19 00:00:00.000000

Añade `users.careers`: las carreras que el usuario elige en el onboarding.

El frontend ya mandaba el campo en `PATCH /users/me`, pero como no existía ni
en el schema ni en la tabla, Pydantic lo descartaba y la respuesta era 200. La
selección sólo vivía en localStorage.

Nullable y sin `server_default`: ya hay filas en `users` y ninguna tiene
carreras que declarar. El `default=list` del modelo cubre las filas nuevas; las
viejas quedan en NULL, que el schema expone como `null` — distinto de `[]`
("elegí y no marqué ninguna") a propósito.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e5f6a7d8c9ab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'careers',
            # Igual que `inferred_skills` en el modelo: JSONB en PostgreSQL y
            # JSON en el resto, para que la suite siga corriendo en SQLite.
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column('users', 'careers')
