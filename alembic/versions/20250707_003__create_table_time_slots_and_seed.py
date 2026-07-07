import uuid
from collections.abc import Sequence
from datetime import time

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from alembic import op

revision: str = '20250707_003'
down_revision: str | None = '20250707_002'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'time_slots',

        sa.Column('id', sa.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('start_time', sa.Time, nullable=False),
        sa.Column('end_time', sa.Time, nullable=False),

        sa.UniqueConstraint('start_time', 'end_time', name='unique_slots'),

        if_not_exists=True
    )

    time_slots = sa.table(
        'time_slots',
        sa.column('id'),
        sa.column('start_time'),
        sa.column('end_time'),
    )
    op.execute(
        insert(time_slots)
        .values(
            [
                {'id': uuid.uuid4(), 'start_time': time(9, 0), 'end_time': time(11, 0)},
                {'id': uuid.uuid4(), 'start_time': time(11, 0), 'end_time': time(13, 0)},
                {'id': uuid.uuid4(), 'start_time': time(14, 0), 'end_time': time(16, 0)},
                {'id': uuid.uuid4(), 'start_time': time(16, 0), 'end_time': time(18, 0)},
            ]
        )
        .on_conflict_do_nothing(index_elements=['start_time', 'end_time']))


def downgrade() -> None:
    op.drop_table('time_slots')
