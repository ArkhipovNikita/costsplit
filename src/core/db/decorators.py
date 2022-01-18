import functools
import inspect
from contextlib import asynccontextmanager
from typing import AsyncContextManager, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.session import transactional_async_scoped_session_factory


def transactional_async_session_maker(
    async_session_factory_: Callable[..., AsyncSession]
) -> Callable[..., AsyncContextManager[AsyncSession]]:
    @asynccontextmanager
    async def wrapper(**kwargs) -> AsyncContextManager[AsyncSession]:
        """Provide a transactional scope around a series of operations."""
        db = async_session_factory_(**kwargs)

        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        else:
            await db.commit()
        finally:
            await db.close()

    return wrapper


def transactional(func):
    """Commit database changes if no exceptions raise otherwise rollback."""

    @functools.wraps(func)
    async def wrap_func(*args, **kwargs):
        async with transactional_async_scoped_session_factory():
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

        return result

    return wrap_func
