from datetime import date

import sqlalchemy as sa

from src.models.base import BaseTable


class Trip(BaseTable):
    __table_args__ = (
        sa.UniqueConstraint('chat_id', 'name'),
    )

    chat_id = sa.Column(sa.Integer, nullable=False)
    name = sa.Column(sa.String, nullable=False, default='')
    is_active = sa.Column(sa.Boolean, nullable=False)
    created_at = sa.Column(sa.Date, nullable=False, default=date.today)
