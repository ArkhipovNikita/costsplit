from aiogram import Dispatcher
from aiogram.utils import executor

from src.config.injector import init_container
from src.loader import dp


async def on_startup(dp_: Dispatcher):
    init_container()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        skip_updates=True,
    )
