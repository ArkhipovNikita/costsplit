from datetime import date
from typing import List, Optional

from pydantic import Field, PositiveFloat

from src.schemes.base import BaseScheme, DBBaseScheme


class PartScheme(BaseScheme):
    participant_id: int
    amount: PositiveFloat


class ExpenseBaseScheme(BaseScheme):
    description: Optional[str] = Field(max_length=255, default='')
    parts: Optional[List[PartScheme]] = Field(default=[])
    created_at: Optional[date]


class ExpenseCreateScheme(ExpenseBaseScheme):
    trip_id: int
    payer_id: int
    amount: PositiveFloat


class ExpenseUpdateScheme(ExpenseBaseScheme):
    payer_id: Optional[int]
    amount: Optional[PositiveFloat]


class ExpenseDBBaseScheme(DBBaseScheme):
    description: str
    parts: List[PartScheme]


class ExpenseScheme(ExpenseDBBaseScheme):
    pass


class ExpenseBScheme(ExpenseDBBaseScheme):
    pass
