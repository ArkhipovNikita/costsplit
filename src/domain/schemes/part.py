from typing import Optional

from pydantic import PositiveFloat

from src.domain.schemes.base import BaseScheme, DBBaseScheme


class PartBaseScheme(BaseScheme):
    pass


class PartCreateScheme(PartBaseScheme):
    expense_id: int
    debtor_id: int
    amount: PositiveFloat


class PartUpdateScheme(PartBaseScheme):
    amount: Optional[PositiveFloat]


class PartDBBaseScheme(DBBaseScheme):
    expense_id: int
    debtor_id: int
    amount: PositiveFloat


class PartScheme(PartDBBaseScheme):
    pass


class PartBScheme(PartDBBaseScheme):
    pass
