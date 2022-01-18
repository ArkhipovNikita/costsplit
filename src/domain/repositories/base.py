from abc import ABC
from typing import Generic, List, Optional, get_args

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.types import (
    CreateSchemaType,
    ModelType,
    UpdateIn,
    UpdateSchemaType,
)
from src.domain.repositories.unpackers import (
    create_scheme_to_attrs,
    update_scheme_to_attrs,
)
from src.utils.attrs import set_attrs


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
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

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create an object."""

        obj = self.__model(**create_scheme_to_attrs(obj_in))
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)

        return obj

    async def create_many(self, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """Create objects."""
        if not objs_in:
            return []

        objs = [self.__model(**create_scheme_to_attrs(obj_in)) for obj_in in objs_in]

        self._session.add_all(objs)
        await self._session.flush()

        for obj in objs:
            await self._session.refresh(obj)

        return objs

    async def update(self, obj: ModelType, obj_in: UpdateIn) -> ModelType:
        """Update object and returned it with refreshed fields."""
        new_attrs = obj_in if isinstance(obj_in, dict) else update_scheme_to_attrs(obj_in)
        set_attrs(obj, **new_attrs)

        self._session.add(obj)
        await self._session.flush()

        return obj

    async def update_by_id(self, obj_id: int, obj_in: UpdateIn) -> ModelType:
        """Update object by id and returned it."""
        new_attrs = obj_in if isinstance(obj_in, dict) else update_scheme_to_attrs(obj_in)

        query = (
            update(self.__model)
            .where(self.__model.id == obj_id)
            .values(**new_attrs)
            .returning(self.__model)
        )

        res = await self._session.execute(query)
        res = res.fetchone()

        return self.__model(**res)

    async def delete(self, obj: ModelType) -> None:
        """Delete an object."""

        await self._session.delete(obj)
        await self._session.flush()
