from typing import Optional

from src.domain.schemes.base import BaseScheme, DBBaseScheme


class ParticipantBaseScheme(BaseScheme):
    pass


class ParticipantCreateScheme(ParticipantBaseScheme):
    trip_id: int
    user_id: int
    first_name: str


class ParticipantUpdateScheme(ParticipantBaseScheme):
    first_name: Optional[str]


class ParticipantDBBaseScheme(DBBaseScheme):
    trip_id: int
    user_id: int
    first_name: str


class ParticipantScheme(ParticipantDBBaseScheme):
    pass


class ParticipantBScheme(ParticipantDBBaseScheme):
    pass
