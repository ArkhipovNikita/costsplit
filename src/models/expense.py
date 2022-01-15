import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from src.models import BaseTable


class Expense(BaseTable):
    # may be got from participant
    trip_id = sa.Column(sa.Integer, sa.ForeignKey('trip.id', ondelete='CASCADE'), nullable=False)
    payer_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('participant.id', ondelete='CASCADE'),
        nullable=False,
    )
    amount = sa.Column(sa.Float, nullable=False)
    description = sa.Column(sa.String(255), nullable=False, default='')
    parts = sa.Column(JSONB, nullable=False, default={})
    created_at = sa.Column(sa.Date)
