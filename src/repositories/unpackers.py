from typing import Any, Dict

from pydantic import BaseModel


def create_scheme_to_attrs(scheme: BaseModel) -> Dict[str, Any]:
    """Get create scheme attrs."""
    return scheme.dict(by_alias=True)


def update_scheme_to_attrs(scheme: BaseModel) -> Dict[str, Any]:
    """Get update scheme attrs."""
    return scheme.dict(exclude_unset=True, by_alias=True)
