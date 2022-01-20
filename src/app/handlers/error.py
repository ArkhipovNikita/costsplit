from aiogram.types import Update
from pydantic import ValidationError

from src.loader import dp


@dp.errors_handler(exception=ValidationError)
async def handle_pydantic_validation_error(update: Update, exception: ValidationError):
    """Error handler for `pydantic.ValidationError`."""
    error_message = '\n'.join([error['msg'] for error in exception.errors()])
    return await update.message.reply(error_message)
