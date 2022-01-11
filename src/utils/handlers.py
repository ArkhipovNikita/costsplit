from aiogram.types import Message
from aiogram_dialog import DialogManager
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.services import TripService


def ensure_trip_exists(handler):
    """Decorator to check that an active trip exists for a chat."""
    @inject
    async def wrapped(
            message: Message,
            dialog_manager: DialogManager,
            trip_service: TripService = Provide[Container.trip_service],
            *args,
            **kwargs,
    ):
        if not await trip_service.exists_by(chat_id=message.chat.id, is_active=True):
            await message.answer('Начните путешествие и добавьте участников')
            return

        return await handler(message, dialog_manager)

    return wrapped
