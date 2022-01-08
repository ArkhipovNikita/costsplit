import operator

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Column, Multiselect
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject
from pyrogram.methods.chats.get_chat_members import Filters

from src.config.injector import Container
from src.config.pyrogram import telegram_client
from src.loader import dp
from src.models import Participant
from src.services import TripService
from src.services.participant import ParticipantService
from src.utils.db import transactional
from src.widgets.keyboards import Multiurl, ZippedColumns


class ParticipantAdd(StatesGroup):
    choosing = State()


async def get_chat_members(dialog_manager: DialogManager, **kwargs):
    chat_id = (
        dialog_manager.event.chat.id
        if isinstance(dialog_manager.event, Message)
        else dialog_manager.event.message.chat.id
    )

    chat_members = await telegram_client.get_chat_members(chat_id, filter=Filters.ALL)

    chat_members = map(lambda u: u.user, chat_members)
    chat_members = filter(lambda u: not u.is_bot, chat_members)
    chat_members = [(user.first_name, user.id) for user in chat_members]

    return {'chat_members': chat_members}


@dp.message_handler(commands=['add_participant'])
@inject
async def add_participant_start(
        message: Message,
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
):
    if not await trip_service.exists_by(chat_id=message.chat.id, is_active=True):
        await message.answer('Начните путешествие и добавьте участников')
        return

    await dialog_manager.start(ParticipantAdd.choosing, mode=StartMode.RESET_STACK)


@inject
@transactional
async def add_participant_finish(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    context = dialog_manager.current_context()
    chosen_participants_ids = context.widget_data[chosen_participants_widget_id]
    chosen_participants = await telegram_client.get_users(chosen_participants_ids)

    current_trip = await trip_service.get_by(chat_id=call.message.chat.id, is_active=True)

    participants = [
        Participant(trip_id=current_trip.id, user_id=user.id, first_name=user.first_name)
        for user in chosen_participants
    ]
    await participant_service.create_many(participants)

    await call.answer('Участники успешно добавлены')
    await dialog_manager.done()


chosen_participants_widget_id = 'chosen_participants'

participants_multiselect = Multiselect(
    Format('{item[0]} ✔'),
    Format('{item[0]}'),
    id=chosen_participants_widget_id,
    item_id_getter=operator.itemgetter(1),
    items='chat_members',
)

participant_links = Multiurl(
    Format('🔗'),
    Format('tg://user?id={item[1]}'),
    items='chat_members',
)

participant_adding_dialog = Dialog(
    Window(
        Const('Выберете участников'),
        ZippedColumns(Column(participants_multiselect), Column(participant_links)),
        Button(
            Const('Закончить 👌'),
            id=chosen_participants_widget_id,
            on_click=add_participant_finish
        ),
        state=ParticipantAdd.choosing,
        getter=get_chat_members,
    ),
)
