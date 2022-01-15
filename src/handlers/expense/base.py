from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject

from src.config import app_settings
from src.config.injector import Container
from src.handlers.consts import CURRENT_EXPENSE_ID, CURRENT_TRIP_ID
from src.handlers.expense.common import ManageExpense
from src.loader import dp
from src.services import ExpenseService, ParticipantService, TripService
from src.utils.handlers import ensure_trip_exists


@dp.message_handler(commands=['expense'])
@ensure_trip_exists
@inject
async def manage_expense_start(
        message: Message,
        dialog_manager: DialogManager,
        trip_service: TripService = Provide[Container.trip_service],
):
    """Create expense and start appropriate dialog."""
    trip = await trip_service.get_active_trip(message.chat.id)

    await dialog_manager.start(
        state=ManageExpense.amount,
        data={CURRENT_TRIP_ID: trip.id},
        mode=StartMode.RESET_STACK,
    )


@inject
async def get_expense_data(
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
        **kwargs
):
    """Get expense data."""
    current_expense_id = dialog_manager.current_context().start_data.get(CURRENT_EXPENSE_ID)
    current_expense = await expense_service.get_by(id=current_expense_id)
    payer = await participant_service.get_by(id=current_expense.payer_id)

    return {
        'amount': current_expense.amount,
        'created_at': current_expense.created_at.strftime(app_settings.date_format) if current_expense.created_at else None,
        'payer': payer.first_name,
    }


base_window = Window(
    Format('Трата: amount={amount}|created_at={created_at}|payer={payer}'),
    SwitchTo(
        Const('Уточнить сумму 💸'),
        id='update_expense_amount',
        state=ManageExpense.amount,
    ),
    SwitchTo(
        Const('Уточнить плательщика 💳'),
        id='update_expense_payer',
        state=ManageExpense.payer,
    ),
    SwitchTo(
      Const('Уточнить доли 🤝'),
      id='update_expense_parts',
      state=ManageExpense.parts_participants,
    ),
    SwitchTo(
        Const('Уточнить описание ✏️'),
        id='update_expense_description',
        state=ManageExpense.description,
    ),
    SwitchTo(
        Const('Уточнить дату 📅'),
        id='update_expense_created_at',
        state=ManageExpense.created_at_shortcut,
    ),
    state=ManageExpense.base,
    getter=get_expense_data,
)
