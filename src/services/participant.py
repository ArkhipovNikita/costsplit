from typing import List

from src.models import Participant
from src.repositories import ParticipantRepository
from src.services.base import BaseService


class ParticipantService(BaseService[Participant, ParticipantRepository]):
    def __init__(self, participant_repository: ParticipantRepository):
        super().__init__(participant_repository)
        self.participant_repository = participant_repository

    async def get_trip_participants_user_ids(self, trip_id: int) -> List[int]:
        """Get user ids of a trip."""
        return await self.participant_repository.get_trip_participants_user_ids(trip_id)

    async def delete_from_trip_by_user_ids(self, trip_id: int, user_ids: List[int]) -> int:
        """Delete participants by user ids from a trip."""
        return await self.participant_repository.delete_from_trip_by_user_ids(trip_id, user_ids)
