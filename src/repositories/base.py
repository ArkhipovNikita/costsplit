from abc import ABC
from typing import Any, Dict, Generic, Optional, TypeVar, get_args

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import BaseTable

ModelType = TypeVar('ModelType', bound=BaseTable)


class BaseRepository(Generic[ModelType], ABC):
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    @property
    def __model(self) -> ModelType:
        return get_args(self.__orig_bases__[0])[0]

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get object by any fields if found else None."""

        query = select(self.__model).filter_by(**kwargs).limit(1)
        res = await self._session.execute(query)
        res = res.scalars().first()

        return res

    async def exists_by(self, **kwargs) -> bool:
        """Check an object existing by any fields."""
        query = select(self.__model).filter_by(**kwargs).limit(1)

        res = await self._session.execute(select(exists(query)))
        res = res.scalars().first()

        return res

    async def create(self, obj: ModelType) -> ModelType:
        """Create an object."""

        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)

        return obj

    async def update(self, obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update object and returned it with refreshed fields."""

        for k, v in obj_in.items():
            setattr(obj, k, v)

        self._session.add(obj)
        await self._session.flush()

        return obj

    async def update_by_id(self, obj_id: int, obj_in: Dict[str, Any]) -> ModelType:
        """Update object by id and returned it."""

        query = (
            update(self.__model)
            .where(self.__model.id == obj_id)
            .values(**obj_in)
            .returning(self.__model)
        )

        res = await self._session.execute(query)
        res = res.fetchone()

        return self.__model(**res)

    async def delete(self, obj: ModelType) -> None:
        """Delete an object."""

        await self._session.delete(obj)
        await self._session.flush()
