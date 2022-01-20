import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Radio
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject

from src.app.keys import CURRENT_EXPENSE_ID, CURRENT_TRIP_ID
from src.app.states import ManageExpense
from src.app.widgets.keyboards import ListUserURL, Zipped
from src.core.db.decorators import transactional
from src.core.injector import Container
from src.domain.schemes.expense import ExpenseUpdateScheme
from src.domain.services import ExpenseService, ParticipantService

PAYER_CHOOSING_WIDGET_ID = 'expense_payer'


@inject
async def get_trip_participants(
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
        **kwargs,
):
    """Get current trip participants and set initial data to a widget."""
    context = dialog_manager.current_context()

    current_trip_id = context.start_data[CURRENT_TRIP_ID]
    current_expense_id = context.start_data[CURRENT_EXPENSE_ID]

    current_expense = await expense_service.get_by(id=current_expense_id)
    current_payer = await participant_service.get_by(id=current_expense.payer_id)

    context.widget_data[PAYER_CHOOSING_WIDGET_ID] = str(current_payer.user_id)

    participants = await participant_service.get_trip_participants(current_trip_id)
    participants = [(p.first_name, p.user_id) for p in participants]

    return {'participants': participants}


@inject
@transactional
async def update_payer(
        call: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Update current expense `payer_id` field."""
    item_id = int(item_id)
    current_expense_id = dialog_manager.current_context().start_data[CURRENT_EXPENSE_ID]

    participant = await participant_service.get_by(user_id=item_id)
    expense_in = ExpenseUpdateScheme(payer_id=participant.id)
    await expense_service.update_by_id(current_expense_id, expense_in)

    await dialog_manager.dialog().switch_to(ManageExpense.base)


payer_window = Window(
    Const('Выберете плательщка'),
    Zipped(
        Column(
            Radio(
                Format('{item[0]} ✔️'),
                Format('{item[0]}'),
                id=PAYER_CHOOSING_WIDGET_ID,
                item_id_getter=operator.itemgetter(1),
                items='participants',
                on_click=update_payer,
            ),
        ),
        Column(ListUserURL(user_id_getter=operator.itemgetter(1), items='participants')),
    ),
    state=ManageExpense.payer,
    getter=get_trip_participants,
)
