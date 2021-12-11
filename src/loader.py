from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from src.config import bot_settings

storage = MemoryStorage()
bot = Bot(token=bot_settings.api_token)
dp = Dispatcher(bot, storage=storage)
