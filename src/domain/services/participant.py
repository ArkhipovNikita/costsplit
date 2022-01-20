from typing import List

from src.domain.models import Participant
from src.domain.repositories import ParticipantRepository
from src.domain.schemes.participant import (
    ParticipantCreateScheme,
    ParticipantUpdateScheme,
)
from src.domain.services.base import BaseService


class ParticipantService(
    BaseService[
        Participant,
        ParticipantRepository,
        ParticipantCreateScheme,
        ParticipantUpdateScheme,
    ],
):
    def __init__(self, participant_repository: ParticipantRepository):
        super().__init__(participant_repository)
        self.participant_repository = participant_repository

    async def get_trip_participants(self, trip_id: int) -> List[Participant]:
        """Get participants of a trip."""
        return await self.participant_repository.get_trip_participants(trip_id)

    async def get_trip_participants_user_ids(self, trip_id: int) -> List[int]:
        """Get user ids of a trip."""
        return await self.participant_repository.get_trip_participants_user_ids(trip_id)

    async def get_participants_by_user_ids(self, user_ids: List[int]) -> List[Participant]:
        """Get participants by user ids."""
        return await self.participant_repository.get_participants_by_user_ids(user_ids)

    async def delete_from_trip_by_user_ids(self, trip_id: int, user_ids: List[int]) -> int:
        """Delete participants by user ids from a trip."""
        return await self.participant_repository.delete_from_trip_by_user_ids(trip_id, user_ids)