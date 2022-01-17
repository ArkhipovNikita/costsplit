from abc import ABC
from typing import Generic, List, Optional, TypeVar

from src.repositories import BaseRepository
from src.repositories.types import (
    CreateSchemaType,
    ModelType,
    UpdateIn,
    UpdateSchemaType,
)

ModelRepositoryType = TypeVar('ModelRepositoryType', bound=BaseRepository)


class BaseService(
    Generic[
        ModelType,
        ModelRepositoryType,
        CreateSchemaType,
        UpdateSchemaType,
    ],
    ABC,
):
    def __init__(self, model_repository: ModelRepositoryType):
        self.__model_repository = model_repository

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get object by any fields if found else None."""
        return await self.__model_repository.get_by(**kwargs)

    async def exists_by(self, **kwargs) -> bool:
        """Check an object existing by any fields."""
        return await self.__model_repository.exists_by(**kwargs)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create an object."""
        return await self.__model_repository.create(obj_in)

    async def create_many(self, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """Create objects."""
        return await self.__model_repository.create_many(objs_in)

    async def update(self, obj: ModelType, obj_in: UpdateIn) -> ModelType:
        """Update object and returned it with refreshed fields."""
        return await self.__model_repository.update(obj, obj_in)

    async def update_by_id(self, obj_id: int, obj_in: UpdateIn) -> ModelType:
        """Update object by id and returned it."""
        return await self.__model_repository.update_by_id(obj_id, obj_in)
