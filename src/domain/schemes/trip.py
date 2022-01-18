from datetime import date
from typing import Optional

from pydantic import Field

from src.domain.schemes.base import BaseScheme, DBBaseScheme


class TripBaseScheme(BaseScheme):
    pass


class TripCreateScheme(TripBaseScheme):
    chat_id: int
    is_active: bool
    name: Optional[str] = Field(max_length=100, default='')
    created_at: Optional[date] = Field(default_factory=date.today)


class TripUpdateScheme(TripBaseScheme):
    is_active: Optional[bool]
    name: Optional[str]


class TripDBBaseScheme(DBBaseScheme):
    chat_id: int
    is_active: bool
    name: str
    created_at: date


class TripScheme(TripDBBaseScheme):
    pass


class TripDBScheme(TripDBBaseScheme):
    pass
