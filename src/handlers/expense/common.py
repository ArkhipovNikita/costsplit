from aiogram.dispatcher.filters.state import State, StatesGroup


class ManageExpense(StatesGroup):
    """States group to manage expense."""

    base = State()
    amount = State()
    payer = State()
    parts_participants = State()
    parts_amounts = State()
    description = State()
    created_at_shortcut = State()
    created_at_calendar = State()
