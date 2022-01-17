from typing import List

from sqlalchemy import and_, delete, select

from src.models import Participant
from src.repositories import BaseRepository
from src.schemes.participant import ParticipantCreateScheme, ParticipantUpdateScheme


class ParticipantRepository(
    BaseRepository[
        Participant,
        ParticipantCreateScheme,
        ParticipantUpdateScheme,
    ],
):
    async def get_trip_participants(self, trip_id: int) -> List[Participant]:
        """Get participants of a trip."""
        query = select(Participant).filter_by(trip_id=trip_id)
        res = await self._session.execute(query)
        res = res.scalars().all()

        return res

    async def get_trip_participants_user_ids(self, trip_id: int) -> List[int]:
        """Get user ids of a trip."""
        query = select(Participant.user_id).filter_by(trip_id=trip_id)
        res = await self._session.execute(query)
        res = res.scalars().all()

        return res

    async def get_participants_by_user_ids(self, user_ids: List[int]) -> List[Participant]:
        """Get participants by user ids."""
        query = select(Participant).where(Participant.user_id.in_(user_ids))
        res = await self._session.execute(query)
        res = res.scalars().all()

        return res

    async def delete_from_trip_by_user_ids(self, trip_id: int, user_ids: List[int]) -> int:
        """Delete participants by user ids from a trip."""
        query = (
            delete(Participant)
            .where(
                and_(
                    Participant.trip_id == trip_id,
                    Participant.user_id.in_(user_ids)
                )
            )
        )

        res = await self._session.execute(query)

        return res.rowcount
