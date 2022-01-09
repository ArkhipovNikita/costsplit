from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.loader import dp
from src.models import Trip
from src.services import TripService
from src.utils.db import transactional


class ManageTrip(StatesGroup):
    base = State()
    name = State()


@dp.message_handler(commands=['start_trip'])
@inject
@transactional
async def start_trip(
        message: types.Message,
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
):
    """Create trip if there is no active trip for current chat."""
    current_trip = await trip_service.get_active_trip_for_chat(chat_id=message.chat.id)

    if current_trip:
        trip_already_exists = True
    else:
        trip_already_exists = False

        current_trip = Trip(chat_id=message.chat.id, is_active=True)
        current_trip = await trip_service.create(current_trip)

    await dialog_manager.start(
        ManageTrip.base,
        data={'current_trip_id': current_trip.id, 'trip_already_exists': trip_already_exists},
        mode=StartMode.RESET_STACK,
    )


@inject
@transactional
async def update_trip_name(
        message: Message,
        dialog: Dialog,
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
):
    """Update trip name."""
    new_trip_name = message.text

    if len(new_trip_name) > 100:
        await message.answer('Название слишком длинное, максимум 100 символов')
        return

    current_trip_id = dialog_manager.current_context().start_data['current_trip_id']
    await trip_service.update_by_id(current_trip_id, {'name': new_trip_name})

    await dialog_manager.dialog().switch_to(ManageTrip.base)


@inject
async def get_data(
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
        **kwargs,
):
    """Get data for current trip."""
    current_trip_id = dialog_manager.current_context().start_data['current_trip_id']
    trip = await trip_service.get_by(id=current_trip_id)

    return {
        'trip_id': trip.id,
        'trip_name': trip.name,
    }


manage_trip_dialog = Dialog(
    Window(
        Case(
            {
                (True, False): Format('Путешествие «{trip_name}» началось ✈️'),
                (False, False): Const('Путешествие началось ✈️'),
                (True, True): Format('Вы уже в путешествии «{trip_name}» 🙌\nДля начала нового – завершите текущее'),  # noqa: E501
                (False, True): Const('Вы уже в путешествии 🙌\nДля начала нового – завершите текущее'),  # noqa: E501
            },
            selector=lambda data, c, m: (
                bool(data['trip_name']),
                m.current_context().start_data['trip_already_exists']
            ),
        ),
        SwitchTo(Const('Уточнить название'), id='update_trip_name', state=ManageTrip.name),
        state=ManageTrip.base,
        getter=get_data,
    ),
    Window(
        Const('Введите новое название'),
        MessageInput(update_trip_name),
        state=ManageTrip.name,
    )
)
