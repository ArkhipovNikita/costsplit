from typing import Any, Dict, TypeVar, Union

from pydantic import BaseModel

from src.domain.models.base import BaseTable

ModelType = TypeVar('ModelType', bound=BaseTable)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
UpdateIn = Union[UpdateSchemaType, Dict[str, Any]]
