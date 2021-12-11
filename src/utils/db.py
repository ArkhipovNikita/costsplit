import functools
import inspect

from src.db.session import transactional_async_scoped_session_factory


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
