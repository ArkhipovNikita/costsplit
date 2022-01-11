from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const
from dependency_injector.wiring import Provide, inject

from src.config.injector import Container
from src.handlers.consts import CURRENT_EXPENSE_ID_KEY
from src.handlers.expense.common import ManageExpense
from src.schemes.expense import ExpenseManualIn
from src.services import ExpenseService
from src.utils.db import transactional


@inject
@transactional
async def update_description(
        message: Message,
        dialog: Dialog,
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
):
    """Validate entered description and update current expense with its value."""
    expense_in = ExpenseManualIn(description=message.text)

    current_expense_id = dialog_manager.current_context().start_data[CURRENT_EXPENSE_ID_KEY]
    await expense_service.update_by_id(current_expense_id, description=expense_in.description)

    await dialog_manager.dialog().switch_to(ManageExpense.base)


description_window = Window(
    Const('Введите описание'),
    MessageInput(update_description),
    state=ManageExpense.description,
)
