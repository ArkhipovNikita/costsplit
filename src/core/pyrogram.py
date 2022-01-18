from pyrogram import Client

from src.core.settings import bot_settings

telegram_client = Client(
    session_name='pyrogram',
    api_id=bot_settings.api_id,
    api_hash=bot_settings.api_hash,
    bot_token=bot_settings.api_token,
)


async def init_telegram_client():
    await telegram_client.__aenter__()


async def close_telegram_client():
    await telegram_client.__aexit__()
