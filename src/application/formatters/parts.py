from typing import Dict

from aiogram.utils import markdown as fmt

from src.application.formatters.common import telegram_user_hmention


def amount_enter(participant: Dict, **kwargs) -> str:
    """Get text for entering part amount."""
    return fmt.text(
        fmt.text('Введите сумму для'),
        telegram_user_hmention(participant['first_name'], participant['user_id']),
    )


def amounts_(amounts: Dict, **kwargs) -> str:
    """Get text for part amounts."""
    texts = []

    for amount in amounts:
        amount['amount'] = str(amount['amount']).rstrip('.0')

        text = fmt.text(
            telegram_user_hmention(amount['first_name'], amount['user_id']),
            fmt.text(': {amount}'),
            sep='',
        ).format(**amount)

        texts.append(text)

    return fmt.text(*texts, sep='\n')


def amounts_already_entered(amounts: Dict, **kwargs) -> str:
    """Get text for already entered part amounts."""
    part_amounts_text = amounts_(amounts)

    text = fmt.text(
        fmt.text('Уже введенные доли'),
        part_amounts_text,
        sep='\n',
    )

    return '<i>{}</i>'.format(text)
