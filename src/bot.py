from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram_dialog import DialogRegistry

from src.core.injector import init_container
from src.core.pyrogram import close_telegram_client, init_telegram_client
from src.handlers.expense import expense_dialog
from src.handlers.participant import manage_participants_dialog
from src.handlers.trip import manage_trip_dialog
from src.loader import dp


async def on_startup(dp_: Dispatcher):
    init_container()
    await init_telegram_client()

    registry = DialogRegistry(dp_)
    registry.register(manage_participants_dialog)
    registry.register(manage_trip_dialog)
    registry.register(expense_dialog)


async def on_shutdown(dp_: Dispatcher):
    await close_telegram_client()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )
