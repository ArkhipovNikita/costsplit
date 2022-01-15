import operator

from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.context.context import Context
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Column, Multiselect, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.handlers.consts import CURRENT_EXPENSE_ID_KEY, CURRENT_TRIP_ID_KEY
from src.handlers.expense.common import ManageExpense
from src.schemes.expense import ExpenseManualIn
from src.services import ExpenseService, ParticipantService
from src.utils.db import transactional
from src.widgets.keyboards import UserMultiurl, Zipped

PARTICIPANTS_CHOOSING_WIDGET_ID = 'expense_parts_participants'
AMOUNTS_WIDGET_ID = 'expense_parts_amounts'

CURRENT_PARTICIPANT_IDX_KEY = 'current_participant_idx'
CHOSEN_PARTICIPANTS_KEY = 'participants'


@inject
async def get_trip_participants_data(
        dialog_manager: DialogManager,
        participant_service: ParticipantService = Provide[Container.participant_service],
        **kwargs,
):
    """Get current trip participants."""
    context = dialog_manager.current_context()
    current_trip_id = context.start_data[CURRENT_TRIP_ID_KEY]

    participants = await participant_service.get_trip_participants(current_trip_id)
    participants = {p.user_id: p.first_name for p in participants}

    return {'participants': participants.items()}


@inject
async def init_parts_amounts_data(
        context: Context,
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Set initial context data for parts amounts widget (step)."""
    chosen_participants_user_ids = context.widget_data[PARTICIPANTS_CHOOSING_WIDGET_ID]
    chosen_participants_user_ids = list(map(int, chosen_participants_user_ids))

    chosen_participants = await participant_service.get_participants_by_user_ids(
        chosen_participants_user_ids,
    )

    chosen_participants = [
        {
            'id': p.id,
            'user_id': p.user_id,
            'first_name': p.first_name,
            'amount': None,
        }
        for p in chosen_participants
    ]

    context.widget_data[AMOUNTS_WIDGET_ID] = {
        CURRENT_PARTICIPANT_IDX_KEY: 0,
        CHOSEN_PARTICIPANTS_KEY: chosen_participants,
    }


async def get_part_participant_data(dialog_manager: DialogManager, **kwargs):
    """Get data about current part participant."""
    context = dialog_manager.current_context()
    parts_amounts_data = context.widget_data.get(AMOUNTS_WIDGET_ID)

    if not parts_amounts_data:
        await init_parts_amounts_data(context)
        parts_amounts_data = context.widget_data[AMOUNTS_WIDGET_ID]

    current_participant_idx = parts_amounts_data[CURRENT_PARTICIPANT_IDX_KEY]
    current_participant_data = parts_amounts_data[CHOSEN_PARTICIPANTS_KEY][current_participant_idx]

    return current_participant_data


@inject
@transactional
async def handle_part_amount(
        message: Message,
        dialog: Dialog,
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
):
    """Validate input amount and save it."""
    expense_in = ExpenseManualIn(part_amount=message.text)

    context = dialog_manager.current_context()
    parts_amounts_data = context.widget_data[AMOUNTS_WIDGET_ID]

    participants = parts_amounts_data[CHOSEN_PARTICIPANTS_KEY]
    current_participant_idx = parts_amounts_data[CURRENT_PARTICIPANT_IDX_KEY]
    current_participant_data = participants[current_participant_idx]

    current_participant_data['amount'] = expense_in.part_amount
    current_participant_idx += 1

    parts_amounts_data[CURRENT_PARTICIPANT_IDX_KEY] = current_participant_idx

    if len(participants) == current_participant_idx:
        participants_amounts = [{p['id']: p['amount']} for p in participants]
        current_expense_id = context.start_data[CURRENT_EXPENSE_ID_KEY]
        await expense_service.update_by_id(current_expense_id, parts=participants_amounts)

        await dialog_manager.switch_to(ManageExpense.base)


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
        # Осталось {remain_amount}
        Format('Введите сумм для {first_name}, '),
        MessageInput(handle_part_amount),
        state=ManageExpense.parts_amounts,
        getter=get_part_participant_data,
    ),
]
