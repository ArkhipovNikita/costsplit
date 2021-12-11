from abc import ABC
from typing import Any, Dict, Generic, Optional, TypeVar

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

    async def create(self, obj: ModelType) -> ModelType:
        """Create an object."""
        return await self.__model_repository.create(obj)

    async def update(self, obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update object and returned it with refreshed fields."""
        return await self.__model_repository.update(obj, obj_in)

    async def update_by_id(self, obj_id: int, obj_in: Dict[str, Any]) -> ModelType:
        """Update object by id and returned it."""
        return await self.__model_repository.update_by_id(obj_id, obj_in)
