import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.domain.models import BaseTable


class Part(BaseTable):
    expense_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('expense.id', ondelete='CASCADE'),
        nullable=False,
    )
    debtor_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('participant.id', ondelete='CASCADE'),
        nullable=False,
    )
    amount = sa.Column(sa.Float, nullable=False)

    expense = relationship('Expense', backref='parts')
