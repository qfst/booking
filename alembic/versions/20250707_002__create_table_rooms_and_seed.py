import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import insert

revision: str = '20250707_002'
down_revision: str | None = '20250707_001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'rooms',

        sa.Column('id', sa.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),

        if_not_exists=True
    )

    rooms = sa.table(
        'rooms',
        sa.column('id'),
        sa.column('name'),
    )
    op.execute(
        insert(rooms)
        .values(
            [
                {'id': uuid.uuid4(), 'name': 'Room A'},
                {'id': uuid.uuid4(), 'name': 'Room B'},
                {'id': uuid.uuid4(), 'name': 'Room C'},
            ]
        )
        .on_conflict_do_nothing(index_elements=['name']))


def downgrade() -> None:
    op.drop_table('rooms')
