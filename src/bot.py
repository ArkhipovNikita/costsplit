from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram_dialog import DialogRegistry

from src.config.injector import init_container
from src.config.pyrogram import close_telegram_client, init_telegram_client
from src.handlers.participant import manage_participants_dialog
from src.loader import dp

registry = DialogRegistry(dp)
registry.register(manage_participants_dialog)


async def on_startup(dp_: Dispatcher):
    init_container()
    await init_telegram_client()


async def on_shutdown(dp_: Dispatcher):
    await close_telegram_client()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )
