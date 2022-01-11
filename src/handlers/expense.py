import operator
from datetime import date, datetime, timedelta
from typing import Any, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Calendar, Radio, Row, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dependency_injector.wiring import Provide, inject

from src.config import app_settings
from src.config.injector import Container
from src.loader import dp
from src.models.expense import Expense
from src.schemes.expense import ExpenseManualIn
from src.services import ExpenseService, ParticipantService, TripService
from src.utils.db import transactional
from src.utils.handlers import ensure_trip_exists


class ManageExpense(StatesGroup):
    base = State()
    amount = State()
    payer = State()
    created_at_shortcut = State()
    created_at_calendar = State()


@inject
async def get_expense_data(
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
        **kwargs
):
    current_expense_id = dialog_manager.current_context().start_data.get('current_expense_id')
    current_expense = await expense_service.get_by(id=current_expense_id)
    payer = await participant_service.get_by(id=current_expense.payer_id)

    return {
        'amount': current_expense.amount,
        'created_at': current_expense.created_at.strftime(app_settings.date_format) if current_expense.created_at else None,
        'payer': payer.first_name,
    }


@inject
async def get_created_at_shortcut_options(
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        **kwargs,
):
    """Get shortcut options for `created_at` field."""
    current_expense_id = dialog_manager.current_context().start_data.get('current_expense_id')
    expense = await expense_service.get_by(id=current_expense_id)

    created_at_options = [
        ('Вчера', (date.today() - timedelta(days=1)).strftime(app_settings.date_format)),
        ('Сегодня', date.today().strftime(app_settings.date_format)),
    ]

    if expense.created_at:
        created_at_options.insert(0, ('Без даты', ''))

    return {
        'created_at_options': created_at_options,
    }


@inject
async def get_trip_participants(
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
        **kwargs,
):
    """Get current trip participants and set initial data to a widget."""
    context = dialog_manager.current_context()

    current_trip_id = context.start_data['current_trip_id']
    current_expense_id = context.start_data['current_expense_id']

    current_expense = await expense_service.get_by(id=current_expense_id)
    current_payer = await participant_service.get_by(id=current_expense.payer_id)

    context.widget_data['expense_payer'] = str(current_payer.user_id)

    participants = await participant_service.get_trip_participants(current_trip_id)
    participants = [(p.first_name, p.user_id) for p in participants]

    return {'participants': participants}


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
        data={'current_trip_id': trip.id},
        mode=StartMode.RESET_STACK,
    )


@inject
@transactional
async def update_expense_amount(
        message: Message,
        dialog: Dialog,
        dialog_manager: DialogManager,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Validate entered amount and update current expense with its value."""
    expense_in = ExpenseManualIn(amount=message.text)

    context = dialog_manager.current_context()
    current_expense_id = context.start_data.get('current_expense_id')

    if current_expense_id:
        await expense_service.update_by_id(current_expense_id, amount=expense_in.amount)
    else:
        current_trip_id = context.start_data['current_trip_id']
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

        context.start_data['current_expense_id'] = expense.id

    await dialog_manager.dialog().switch_to(ManageExpense.base)


@inject
@transactional
async def update_expense_created_at(
        dialog_manager: DialogManager,
        selected_date: Optional[date],
        expense_service: ExpenseService = Provide[Container.expense_service],
):
    """Update current expense `created_at` field."""
    context = dialog_manager.current_context()
    current_expense_id = context.start_data.get('current_expense_id')

    await expense_service.update_by_id(current_expense_id, created_at=selected_date)
    await dialog_manager.switch_to(ManageExpense.base)


async def update_expense_created_at_calendar(
        call: CallbackQuery,
        widget,
        dialog_manager: DialogManager,
        selected_date: date,
):
    """Update current expense `created_at` field with value got from `Calendar` widget."""
    await update_expense_created_at(dialog_manager, selected_date)


async def update_expense_created_at_shortcut(
        call: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
):
    """Update current expense `created_at` field with value got from shortcuts."""
    selected_date = datetime.strptime(item_id, app_settings.date_format).date() if item_id else None
    await update_expense_created_at(dialog_manager, selected_date)


@inject
@transactional
async def update_expense_payer(
        call: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
        expense_service: ExpenseService = Provide[Container.expense_service],
        participant_service: ParticipantService = Provide[Container.participant_service],
):
    """Update current expense `payer_id` field."""
    item_id = int(item_id)
    current_expense_id = dialog_manager.current_context().start_data['current_expense_id']

    participant = await participant_service.get_by(user_id=item_id)
    await expense_service.update_by_id(current_expense_id, payer_id=participant.id)

    await dialog_manager.dialog().switch_to(ManageExpense.base)


manage_expense_dialog = Dialog(
    Window(
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
            Const('Уточнить дату 📅'),
            id='update_expense_created_at',
            state=ManageExpense.created_at_shortcut
        ),
        state=ManageExpense.base,
        getter=get_expense_data,
    ),
    Window(
        Const('Введите сумму траты'),
        MessageInput(update_expense_amount),
        state=ManageExpense.amount,
    ),
    Window(
        Const('Выберете плательщка'),
        Radio(
            Format('{item[0]} ✔️'),
            Format('{item[0]}'),
            id='expense_payer',
            item_id_getter=operator.itemgetter(1),
            items='participants',
            on_click=update_expense_payer,
        ),
        state=ManageExpense.payer,
        getter=get_trip_participants,
    ),
    Window(
        Const('Выберете дату'),
        Row(
            Select(
                Format('{item[0]}'),
                id='expense_created_at_shortcut',
                item_id_getter=operator.itemgetter(1),
                items='created_at_options',
                on_click=update_expense_created_at_shortcut,
            ),
            SwitchTo(
                Const('Больше ➡️'),
                id='show_more_date_options',
                state=ManageExpense.created_at_calendar,
            ),
        ),
        getter=get_created_at_shortcut_options,
        state=ManageExpense.created_at_shortcut,
    ),
    Window(
        Const('Выберете дату'),
        # TODO: translate to Russian
        Calendar(id='expense_created_at_calendar', on_click=update_expense_created_at_calendar),
        state=ManageExpense.created_at_calendar,
    ),
)
