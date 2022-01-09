from src.models import Trip
from src.repositories import BaseRepository


class TripRepository(BaseRepository[Trip]):
    async def get_active_trip_for_chat(self, chat_id: int) -> Trip:
        """Get active trip for a chat."""
        return await self.get_by(chat_id=chat_id, is_active=True)
