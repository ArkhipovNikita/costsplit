from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const
from dependency_injector.wiring import Provide, inject

from src.app.keys import CURRENT_EXPENSE_ID
from src.app.states import ManageExpense
from src.core.db.decorators import transactional
from src.core.injector import Container
from src.domain.schemes.expense import ExpenseUpdateScheme
from src.domain.services import ExpenseService


@inject
@transactional
async def update_description(
        message: Message,
        dialog: Dialog,
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
):
    """Validate entered description and update current expense with its value."""
    expense_in = ExpenseUpdateScheme(description=message.text)

    current_expense_id = dialog_manager.current_context().start_data[CURRENT_EXPENSE_ID]
    await expense_service.update_by_id(current_expense_id, expense_in)

    await dialog_manager.dialog().switch_to(ManageExpense.base)


description_window = Window(
    Const('Введите описание'),
    MessageInput(update_description),
    state=ManageExpense.description,
)
