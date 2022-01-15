from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.handlers.consts import CURRENT_EXPENSE_ID, CURRENT_TRIP_ID
from src.handlers.expense.common import ManageExpense
from src.models import Expense
from src.schemes.expense import ExpenseManualIn
from src.services import ExpenseService, ParticipantService
from src.utils.db import transactional


@inject
@transactional
async def update_amount(
        message: Message,
        dialog: Dialog,
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Validate entered amount and update current expense with its value."""
    expense_in = ExpenseManualIn(amount=message.text)

    context = dialog_manager.current_context()
    current_expense_id = context.start_data.get(CURRENT_EXPENSE_ID)

    if current_expense_id:
        await expense_service.update_by_id(current_expense_id, amount=expense_in.amount)
    else:
        current_trip_id = context.start_data[CURRENT_TRIP_ID]
        participant = await participant_service.get_by(
            trip_id=current_trip_id,
            user_id=message.from_user.id,
        )

        expense = Expense(
            trip_id=current_trip_id,
            payer_id=participant.id,
            amount=expense_in.amount,
        )
        await expense_service.create(expense)

        context.start_data[CURRENT_EXPENSE_ID] = expense.id

    await dialog_manager.dialog().switch_to(ManageExpense.base)


amount_window = Window(
    Const('Введите сумму траты'),
    MessageInput(update_amount),
    state=ManageExpense.amount,
)
