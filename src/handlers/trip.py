from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.formatters.trip import trip_already_started_fmt, trip_base_fmt
from src.keyboards.trip import trip_base_cb, trip_base_keyboard
from src.loader import bot, dp
from src.models import Trip
from src.services import TripService
from src.utils.db import transactional


class TripUpdate(StatesGroup):
    name = State()


@dp.message_handler(commands=['start_trip'])
@inject
@transactional
async def start_trip(
        message: types.Message,
        trip_service: TripService = Provide[Container.trip_service],
):
    if await trip_service.exists_by(
            chat_id=message.chat.id,
            is_active=True,
    ):
        await message.answer(trip_already_started_fmt(), parse_mode='HTML')
        return

    trip = Trip(chat_id=message.chat.id, is_active=True)
    trip = await trip_service.create(trip)

    await message.answer(
        text=trip_base_fmt(trip),
        reply_markup=trip_base_keyboard(trip),
        parse_mode='HTML',
    )


@dp.callback_query_handler(trip_base_cb.filter())
async def update_trip_name_start(
        call: types.CallbackQuery,
        callback_data: dict,
):
    await TripUpdate.name.set()
    state = dp.get_current().current_state()
    await state.update_data(trip_id=int(callback_data['id']), message_id=call.message.message_id)

    await bot.send_message(call.message.chat.id, 'Введите новое название')
    await call.answer()


@dp.message_handler(state=TripUpdate.name)
@inject
@transactional
async def update_trip_name_finish(
        message: types.Message,
        state: FSMContext,
        trip_service: TripService = Provide[Container.trip_service],
):
    new_trip_name = message.text

    if len(new_trip_name) > 100:
        await message.answer('Название слишком длинное, максимум 100 символов')
        return
    if await trip_service.exists_by(name=new_trip_name):
        await message.answer('Путешествие с таким названием уже существует')
        return

    state_data = await state.get_data()

    trip = await trip_service.update_by_id(state_data['trip_id'], {'name': new_trip_name})

    await bot.edit_message_text(
        text=trip_base_fmt(trip),
        reply_markup=trip_base_keyboard(trip),
        chat_id=message.chat.id,
        message_id=state_data['message_id'],
        parse_mode='HTML',
    )
    await state.finish()
