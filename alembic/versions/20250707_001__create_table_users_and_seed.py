import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from alembic import op
from app.core.security import hash_password


revision: str = '20250707_001'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'users',

        sa.Column(
            'id',
            sa.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
        ),
        sa.Column('login', sa.String(length=50), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=False),

        if_not_exists=True
    )

    time_slots = sa.table(
        'users',
        sa.column('id'),
        sa.column('login'),
        sa.column('password'),
        sa.column('role'),
    )

    op.execute(
        insert(time_slots)
        .values(
            [
                {
                    'id': uuid.uuid4(),
                    'login': 'admin',
                    'password': hash_password('admin'),
                    'role': 'admin'
                },
                {
                    'id': uuid.uuid4(),
                    'login': 'employee',
                    'password': hash_password('employee'),
                    'role': 'employee'
                },
            ]
        )
    )


def downgrade() -> None:
    op.drop_table('users')
