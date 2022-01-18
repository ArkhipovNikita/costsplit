from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from src.core.settings import postgres_settings
from src.core.db.decorators import transactional_async_session_maker

async_engine = create_async_engine(postgres_settings.async_url)
async_session_factory = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
async_scoped_session_factory = async_scoped_session(async_session_factory, scopefunc=current_task)
transactional_async_session_factory = transactional_async_session_maker(async_session_factory)
transactional_async_scoped_session_factory = transactional_async_session_maker(
    async_scoped_session_factory
)
