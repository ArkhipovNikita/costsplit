from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.formatters import trip as trip_fmts
from src.keyboards import trip as trip_keyboards
from src.keyboards.common import empty_keyboard
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
    if await trip_service.get_by(
            chat_id=message.chat.id,
            is_active=True,
    ):
        await message.answer(trip_fmts.already_started(), parse_mode='HTML')
        return

    trip = Trip(chat_id=message.chat.id, is_active=True)
    trip = await trip_service.create(trip)

    await message.answer(
        text=trip_fmts.base(trip),
        reply_markup=trip_keyboards.base(trip),
        parse_mode='HTML',
    )


@dp.message_handler(commands=['cancel'], state=TripUpdate.all_states)
@inject
async def cancel(message: types.Message, state: FSMContext,
                 trip_service: TripService = Provide[Container.trip_service], ):
    state_data = await state.get_data()

    trip = await trip_service.get_by(id=state_data['trip_id'])

    await message.answer('Операция отменена.')
    await bot.edit_message_text(
        text=trip_fmts.base(trip),
        reply_markup=trip_keyboards.base(trip),
        chat_id=message.chat.id,
        message_id=state_data['message_id'],
        parse_mode='HTML',
    )
    await state.finish()


@dp.callback_query_handler(trip_keyboards.cb.filter())
async def update_trip_name_start(
        call: types.CallbackQuery,
        callback_data: dict,
):
    # TODO: check for trip existing
    message_id, chat_id = call.message.message_id, call.message.chat.id

    await TripUpdate.name.set()
    state = dp.get_current().current_state()
    await state.update_data(trip_id=int(callback_data['id']), message_id=message_id)

    await bot.edit_message_reply_markup(
        reply_markup=empty_keyboard,
        chat_id=chat_id,
        message_id=message_id,
    )
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
    # TODO: check for name existing and check length
    state_data = await state.get_data()

    trip = await trip_service.update_by_id(state_data['trip_id'], {'name': message.text})

    await bot.edit_message_text(
        text=trip_fmts.base(trip),
        reply_markup=trip_keyboards.base(trip),
        chat_id=message.chat.id,
        message_id=state_data['message_id'],
        parse_mode='HTML',
    )
    await state.finish()