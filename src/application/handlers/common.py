from aiogram import types
from aiogram.dispatcher import FSMContext
from dependency_injector.wiring import inject

from src.loader import dp


@dp.message_handler(commands=['cancel'], state='*')
@inject
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Операция отменена')
    await state.finish()
