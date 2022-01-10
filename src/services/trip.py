from src.models import Trip
from src.repositories import TripRepository
from src.services.base import BaseService


class TripService(BaseService[Trip, TripRepository]):
    def __init__(self, trip_repository: TripRepository):
        super().__init__(trip_repository)
        self.trip_repository = trip_repository

    async def get_active_trip(self, chat_id: int) -> Trip:
        """Get active trip for a chat."""
        return await self.trip_repository.get_active_trip(chat_id=chat_id)
