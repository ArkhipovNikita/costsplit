import operator
from typing import Any

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.utils import get_chat
from aiogram_dialog.widgets.kbd import Button, Column, Multiselect
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject
from pyrogram.methods.chats.get_chat_members import Filters

from src.core.db.decorators import transactional
from src.core.injector import Container
from src.core.pyrogram import telegram_client
from src.loader import dp
from src.schemes.participant import ParticipantCreateScheme
from src.services import TripService
from src.services.participant import ParticipantService
from src.widgets.keyboards import ListUserURL, Zipped


class ManageParticipant(StatesGroup):
    choosing = State()


async def get_chat_members(dialog_manager: DialogManager, **kwargs):
    """Get chat user members."""
    chat = get_chat(dialog_manager.event)

    chat_members = await telegram_client.get_chat_members(chat.id, filter=Filters.ALL)

    chat_members = map(lambda u: u.user, chat_members)
    chat_members = filter(lambda u: not u.is_bot, chat_members)
    chat_members = [(user.first_name, user.id) for user in chat_members]

    return {'chat_members': chat_members}


@inject
async def mark_already_chosen_participants(
        data: Any,
        dialog_manager: DialogManager,
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Mark already chosen participants in the widget."""
    context = dialog_manager.current_context()

    current_trip_id = context.start_data['current_trip_id']
    chosen_participants = await participant_service.get_trip_participants_user_ids(current_trip_id)

    chosen_participants = list(map(str, chosen_participants))
    context.widget_data[CHOOSING_PARTICIPANTS_WIDGET_ID] = chosen_participants


@dp.message_handler(commands=['manage_participants'])
@inject
async def manage_participants_start(
        message: Message,
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
):
    """Start a process of choosing participants."""
    current_trip = await trip_service.get_by(chat_id=message.chat.id, is_active=True)

    if not current_trip:
        await message.answer('Начните путешествие и добавьте участников')
        return

    await dialog_manager.start(
        state=ManageParticipant.choosing,
        data={'current_trip_id': current_trip.id},
        mode=StartMode.RESET_STACK,
    )


@inject
@transactional
async def manage_participants_finish(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Handle chosen participants."""
    context = dialog_manager.current_context()
    current_trip_id = context.start_data['current_trip_id']

    new_participants = context.widget_data[CHOOSING_PARTICIPANTS_WIDGET_ID]
    new_participants = list(map(int, new_participants))

    old_participants = await participant_service.get_trip_participants_user_ids(current_trip_id)

    new_participants = set(new_participants)
    old_participants = set(old_participants)

    participants_to_delete = list(old_participants - new_participants)
    participants_to_add = list(new_participants - old_participants)

    new_participants = await telegram_client.get_users(participants_to_add)
    new_participants = [
        ParticipantCreateScheme(
            trip_id=current_trip_id,
            user_id=user.id,
            first_name=user.first_name,
        )
        for user in new_participants
    ]

    await participant_service.delete_from_trip_by_user_ids(current_trip_id, participants_to_delete)
    await participant_service.create_many(new_participants)

    await call.message.answer('Участиники успешно изменены')
    await dialog_manager.done()


CHOOSING_PARTICIPANTS_WIDGET_ID = 'CHOOSING_PARTICIPANTS'

participants_multiselect = Multiselect(
    Format('{item[0]} ✔'),
    Format('{item[0]}'),
    id=CHOOSING_PARTICIPANTS_WIDGET_ID,
    item_id_getter=operator.itemgetter(1),
    items='chat_members',
)

participant_links = ListUserURL(user_id_getter=operator.itemgetter(1), items='chat_members')

manage_participants_dialog = Dialog(
    Window(
        Const('Выберете участников'),
        Zipped(Column(participants_multiselect), Column(participant_links)),
        Button(
            Const('Закончить 👌'),
            id=CHOOSING_PARTICIPANTS_WIDGET_ID,
            on_click=manage_participants_finish
        ),
        state=ManageParticipant.choosing,
        getter=get_chat_members,
    ),
    on_start=mark_already_chosen_participants,
)
