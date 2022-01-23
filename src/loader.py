from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.core.settings import bot_settings, redis_settings

storage = RedisStorage2(
    host=redis_settings.host,
    port=redis_settings.port,
    password=redis_settings.password,
    db=redis_settings.db,
    pool_size=10,
)
bot = Bot(token=bot_settings.api_token)
dp = Dispatcher(bot, storage=storage)
