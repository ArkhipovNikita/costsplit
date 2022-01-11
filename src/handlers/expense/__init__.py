from aiogram_dialog import Dialog

from src.handlers.expense.amount import manage_amount_window
from src.handlers.expense.base import base_window
from src.handlers.expense.created_at import manage_created_at_windows
from src.handlers.expense.payer import manage_payer_window

__all__ = ('manage_expense_dialog', )

manage_expense_dialog = Dialog(
    base_window,
    manage_amount_window,
    manage_payer_window,
    *manage_created_at_windows,
)
