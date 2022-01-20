from aiogram_dialog import Dialog

from src.app.handlers.expense.amount import amount_window
from src.app.handlers.expense.base import base_window
from src.app.handlers.expense.created_at import created_at_windows
from src.app.handlers.expense.description import description_window
from src.app.handlers.expense.parts import parts_windows
from src.app.handlers.expense.payer import payer_window

__all__ = ('expense_dialog',)

expense_dialog = Dialog(
    base_window,
    amount_window,
    payer_window,
    description_window,
    *parts_windows,
    *created_at_windows,
)
