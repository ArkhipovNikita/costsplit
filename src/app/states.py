from aiogram.dispatcher.filters.state import State, StatesGroup


class ManageTrip(StatesGroup):
    base = State()
    name = State()


class ManageParticipant(StatesGroup):
    choosing = State()


class ManageExpense(StatesGroup):
    base = State()
    amount = State()
    payer = State()
    parts_participants = State()
    parts_amounts = State()
    description = State()
    created_at_shortcut = State()
    created_at_calendar = State()
