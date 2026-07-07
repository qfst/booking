from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = '20250707_004'
down_revision: str | None = '20250707_003'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'bookings',

        sa.Column('id', sa.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('room_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('slot_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),

        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['slot_id'], ['time_slots.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        sa.UniqueConstraint('date', 'slot_id', 'room_id', name='unique_booking'),

        if_not_exists=True
    )

def downgrade() -> None:
    op.drop_table('bookings')
