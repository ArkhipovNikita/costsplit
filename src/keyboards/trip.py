from aiogram import types
from aiogram.utils.callback_data import CallbackData

from src.models import Trip

trip_base_cb = CallbackData('trip', 'id')


def trip_base_keyboard(trip: Trip) -> types.InlineKeyboardMarkup:
    buttons = [
        types.InlineKeyboardButton(text='Уточнить название', callback_data=trip_base_cb.new(id=trip.id)),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    return keyboard
