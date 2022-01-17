from src.models import Trip
from src.repositories import BaseRepository
from src.schemes.trip import TripCreateScheme, TripUpdateScheme


class TripRepository(BaseRepository[Trip, TripCreateScheme, TripUpdateScheme]):
    async def get_active_trip(self, chat_id: int) -> Trip:
        """Get active trip for a chat."""
        return await self.get_by(chat_id=chat_id, is_active=True)
