from datetime import date
from typing import List, Optional

from pydantic import Field, PositiveFloat

from src.domain.schemes.base import BaseScheme, DBBaseScheme
from src.domain.schemes.part import PartDBScheme
from src.domain.schemes.participant import ParticipantDBScheme


class ExpenseBaseScheme(BaseScheme):
    description: Optional[str] = Field(max_length=255, default='')
    created_at: Optional[date]


class ExpenseCreateScheme(ExpenseBaseScheme):
    trip_id: int
    payer_id: int
    amount: PositiveFloat


class ExpenseUpdateScheme(ExpenseBaseScheme):
    payer_id: Optional[int]
    amount: Optional[PositiveFloat]


class ExpenseDBBaseScheme(ExpenseBaseScheme, DBBaseScheme):
    trip_id: int
    payer_id: int
    amount: PositiveFloat


class ExpenseScheme(ExpenseDBBaseScheme):
    pass


class ExpenseDBScheme(ExpenseDBBaseScheme):
    payer: Optional[ParticipantDBScheme]
    parts: Optional[List[PartDBScheme]]
