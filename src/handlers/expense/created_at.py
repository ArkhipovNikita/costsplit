import operator
from datetime import date, datetime, timedelta
from typing import Any, Optional

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Calendar, Row, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject

from src.config import app_settings
from src.config.injector import Container
from src.handlers.consts import CURRENT_EXPENSE_ID
from src.handlers.expense.common import ManageExpense
from src.schemes.expense import ExpenseUpdateScheme
from src.services import ExpenseService
from src.utils.db import transactional


@inject
async def get_created_at_shortcut_options(
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        **kwargs,
):
    """Get shortcut options for `created_at` field."""
    current_expense_id = dialog_manager.current_context().start_data.get(CURRENT_EXPENSE_ID)
    expense = await expense_service.get_by(id=current_expense_id)

    created_at_options = []

    if expense.created_at:
        created_at_options.insert(0, ('Без даты', ''))

    created_at_options.extend([
        ('Вчера', (date.today() - timedelta(days=1)).strftime(app_settings.date_format)),
        ('Сегодня', date.today().strftime(app_settings.date_format)),
    ])

    return {'created_at_options': created_at_options}


@inject
@transactional
async def update_created_at(
        dialog_manager: DialogManager,
        selected_date: Optional[date],
        expense_service: ExpenseService = Provide[Container.expense_service],
):
    """Update current expense `created_at` field."""
    context = dialog_manager.current_context()
    current_expense_id = context.start_data.get(CURRENT_EXPENSE_ID)

    expense_in = ExpenseUpdateScheme(created_at=selected_date)
    await expense_service.update_by_id(current_expense_id, expense_in)
    await dialog_manager.switch_to(ManageExpense.base)


async def update_created_at_calendar(
        call: CallbackQuery,
        widget,
        dialog_manager: DialogManager,
        selected_date: date,
):
    """Update current expense `created_at` field with value got from `Calendar` widget."""
    await update_created_at(dialog_manager, selected_date)


async def update_created_at_shortcut(
        call: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
):
    """Update current expense `created_at` field with value got from shortcuts."""
    selected_date = datetime.strptime(item_id, app_settings.date_format).date() if item_id else None
    await update_created_at(dialog_manager, selected_date)


created_at_windows = [
    Window(
        Const('Выберете дату'),
        Row(
            Select(
                Format('{item[0]}'),
                id='expense_created_at_shortcut',
                item_id_getter=operator.itemgetter(1),
                items='created_at_options',
                on_click=update_created_at_shortcut,
            ),
            SwitchTo(
                Const('Больше ➡️'),
                id='expense_show_more_created_at_options',
                state=ManageExpense.created_at_calendar,
            ),
        ),
        getter=get_created_at_shortcut_options,
        state=ManageExpense.created_at_shortcut,
    ),
    Window(
        Const('Выберете дату'),
        # TODO: translate to Russian
        Calendar(id='expense_created_at_calendar', on_click=update_created_at_calendar),
        state=ManageExpense.created_at_calendar,
    ),
]
