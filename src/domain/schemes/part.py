from typing import Optional

from pydantic import PositiveFloat

from src.domain.schemes.base import BaseScheme, DBBaseScheme
from src.domain.schemes.participant import ParticipantDBScheme


class PartBaseScheme(BaseScheme):
    pass


class PartCreateScheme(PartBaseScheme):
    expense_id: int
    debtor_id: int
    amount: PositiveFloat


class PartUpdateScheme(PartBaseScheme):
    amount: Optional[PositiveFloat]


class PartDBBaseScheme(PartBaseScheme, DBBaseScheme):
    expense_id: int
    debtor_id: int
    amount: PositiveFloat


class PartScheme(PartDBBaseScheme):
    pass


class PartDBScheme(PartDBBaseScheme):
    debtor: Optional[ParticipantDBScheme]
