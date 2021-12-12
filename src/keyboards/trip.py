from aiogram import types
from aiogram.utils.callback_data import CallbackData

from src.models import Trip

cb = CallbackData('trip', 'id')


def base(trip: Trip) -> types.InlineKeyboardMarkup:
    buttons = [
        types.InlineKeyboardButton(text='Уточнить название', callback_data=cb.new(id=trip.id)),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    return keyboard
