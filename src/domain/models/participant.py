import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.domain.models import BaseTable


class Participant(BaseTable):
    __table_args__ = (
        sa.UniqueConstraint('trip_id', 'user_id'),
    )

    trip_id = sa.Column(sa.Integer, sa.ForeignKey('trip.id', ondelete='CASCADE'), nullable=False)
    user_id = sa.Column(sa.BigInteger, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)

    expenses = relationship('Expense', back_populates='payer')
    parts = relationship('Part', back_populates='debtor')
