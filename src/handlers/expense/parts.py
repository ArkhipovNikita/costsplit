import operator

from aiogram.types import CallbackQuery, Message, ParseMode
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.context.context import Context
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Column, Multiselect, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.formatters import parts as parts_fmt
from src.handlers.consts import CURRENT_EXPENSE_ID, CURRENT_TRIP_ID
from src.handlers.expense.common import ManageExpense
from src.schemes.expense import ExpenseManualIn
from src.services import ExpenseService, ParticipantService
from src.utils.db import transactional
from src.widgets.keyboards import UserMultiurl, Zipped
from src.widgets.texts import Callable

PARTICIPANTS_CHOOSING_WIDGET_ID = 'expense_parts_participants'
AMOUNTS_WIDGET_ID = 'expense_parts_amounts'

PARTICIPANTS = 'participants'
CURRENT_PARTICIPANT_IDX = 'current_participant_idx'
LAST_COMPLETED_PARTICIPANT_IDX = 'last_completed_participant_idx'


@inject
async def get_trip_participants_data(
        manager: DialogManager,
        participant_service: ParticipantService = Provide[Container.participant_service],
        **kwargs,
):
    """Get current trip participants."""
    context = manager.current_context()
    current_trip_id = context.start_data[CURRENT_TRIP_ID]

    participants = await participant_service.get_trip_participants(current_trip_id)
    participants = {p.user_id: p.first_name for p in participants}

    return {'participants': participants.items()}


@inject
async def init_amounts_data(
        context: Context,
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Set initial context data for parts amounts widget (step)."""
    participants_user_ids = context.widget_data[PARTICIPANTS_CHOOSING_WIDGET_ID]
    participants_user_ids = list(map(int, participants_user_ids))

    participants = await participant_service.get_participants_by_user_ids(
        participants_user_ids,
    )

    participants = [
        {
            'user_id': p.user_id,
            'first_name': p.first_name,
            'amount': None,
        }
        for p in participants
    ]

    context.widget_data[AMOUNTS_WIDGET_ID] = {
        CURRENT_PARTICIPANT_IDX: 0,
        LAST_COMPLETED_PARTICIPANT_IDX: -1,
        PARTICIPANTS: participants,
    }


async def get_amounts_data(manager: DialogManager, **kwargs):
    """Get data about participants amounts."""
    context = manager.current_context()
    amounts_data = context.widget_data.get(AMOUNTS_WIDGET_ID)

    if not amounts_data:
        await init_amounts_data(context)
        amounts_data = context.widget_data[AMOUNTS_WIDGET_ID]

    participants = amounts_data[PARTICIPANTS]
    current_participant_idx = amounts_data[CURRENT_PARTICIPANT_IDX]
    current_participant_data = participants[current_participant_idx]

    last_completed_participant_idx = amounts_data[LAST_COMPLETED_PARTICIPANT_IDX]
    completed_participants = participants[:last_completed_participant_idx + 1]

    return {
        'participant': current_participant_data,
        'amounts': completed_participants,
        'meta': {
            CURRENT_PARTICIPANT_IDX: current_participant_idx,
            LAST_COMPLETED_PARTICIPANT_IDX: last_completed_participant_idx,
        },
    }


@inject
@transactional
async def update_expense_parts(
        manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
):
    """Update current expense `parts` field."""
    context = manager.current_context()
    current_expense_id = context.start_data[CURRENT_EXPENSE_ID]
    amounts_data = context.widget_data[AMOUNTS_WIDGET_ID]

    participants = amounts_data[PARTICIPANTS]
    amounts = [
        {
            'participant_user_id': p['user_id'],
            'amount': p['amount'],
        }
        for p in participants
    ]

    await expense_service.update_by_id(current_expense_id, parts=amounts)


async def handle_amount(
        message: Message,
        dialog: Dialog,
        manager: DialogManager,
):
    """Validate input amount and save it."""
    expense_in = ExpenseManualIn(part_amount=message.text)

    context = manager.current_context()
    amounts_data = context.widget_data[AMOUNTS_WIDGET_ID]

    participants = amounts_data[PARTICIPANTS]
    current_participant_idx = amounts_data[CURRENT_PARTICIPANT_IDX]
    current_participant_data = participants[current_participant_idx]

    last_completed_participant_idx = amounts_data[LAST_COMPLETED_PARTICIPANT_IDX]
    amounts_data[LAST_COMPLETED_PARTICIPANT_IDX] = max(
        last_completed_participant_idx, current_participant_idx)

    current_participant_data['amount'] = expense_in.part_amount
    current_participant_idx += 1

    amounts_data[CURRENT_PARTICIPANT_IDX] = current_participant_idx

    if len(participants) == current_participant_idx:
        await update_expense_parts(manager)
        await manager.switch_to(ManageExpense.base)


async def set_previous_participant(call: CallbackQuery, button: Button, manager: DialogManager):
    """Set `CURRENT_PARTICIPANT_IDX` to previous part participant."""
    manager.current_context().widget_data[AMOUNTS_WIDGET_ID][CURRENT_PARTICIPANT_IDX] -= 1


async def set_next_participant(call: CallbackQuery, button: Button, manager: DialogManager):
    """Set `CURRENT_PARTICIPANT_IDX` to next part participant."""
    manager.current_context().widget_data[AMOUNTS_WIDGET_ID][CURRENT_PARTICIPANT_IDX] += 1


parts_windows = [
    Window(
        Const('Выберете участников'),
        Zipped(
            Column(
                Multiselect(
                    Format('{item[1]} ✔️'),
                    Format('{item[1]}'),
                    id=PARTICIPANTS_CHOOSING_WIDGET_ID,
                    item_id_getter=operator.itemgetter(0),
                    items='participants',
                ),
            ),
            Column(UserMultiurl(user_id_pos=1, items='participants')),
        ),
        SwitchTo(
            Const('Выбрать 👌'),
            id='finish_choosing_expense_parts_participants',
            state=ManageExpense.parts_amounts,
        ),
        getter=get_trip_participants_data,
        state=ManageExpense.parts_participants,
    ),
    Window(
        Callable(parts_fmt.amount_enter),
        Multi(
            Const(' '),
            Callable(parts_fmt.amounts_already_entered),
            when=lambda data, w, m: data['meta'][LAST_COMPLETED_PARTICIPANT_IDX] >= 0,
        ),
        Button(
            Const('⬅️ Назад'),
            id='go_to_previous_participant',
            on_click=set_previous_participant,
            when=lambda data, w, m: data['meta'][CURRENT_PARTICIPANT_IDX] > 0,
        ),
        Button(
            Const('Вперед ➡️'),
            id='go_to_next_participant',
            on_click=set_next_participant,
            when=lambda data, w, m: data['meta'][LAST_COMPLETED_PARTICIPANT_IDX] >
                                    data['meta'][CURRENT_PARTICIPANT_IDX],
        ),
        MessageInput(handle_amount),
        state=ManageExpense.parts_amounts,
        getter=get_amounts_data,
        parse_mode=ParseMode.HTML,
    ),
]
