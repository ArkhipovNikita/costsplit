from abc import ABC
from typing import Generic, List, Optional, TypeVar

from src.models import BaseTable
from src.repositories import BaseRepository

ModelType = TypeVar('ModelType', bound=BaseTable)
ModelRepositoryType = TypeVar('ModelRepositoryType', bound=BaseRepository)


class BaseService(Generic[ModelType, ModelRepositoryType], ABC):
    def __init__(self, model_repository: ModelRepositoryType):
        self.__model_repository = model_repository

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get object by any fields if found else None."""
        return await self.__model_repository.get_by(**kwargs)

    async def exists_by(self, **kwargs) -> bool:
        """Check an object existing by any fields."""
        return await self.__model_repository.exists_by(**kwargs)

    async def create(self, obj: ModelType) -> ModelType:
        """Create an object."""
        return await self.__model_repository.create(obj)

    async def create_many(self, objs: List[ModelType]) -> List[ModelType]:
        """Create objects."""
        return await self.__model_repository.create_many(objs)

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        """Update object and returned it with refreshed fields."""
        return await self.__model_repository.update(obj, **kwargs)

    async def update_by_id(self, obj_id: int, **kwargs) -> ModelType:
        """Update object by id and returned it."""
        return await self.__model_repository.update_by_id(obj_id, **kwargs)
