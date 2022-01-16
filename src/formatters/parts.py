from typing import Dict

from aiogram.utils import markdown as fmt

from src.formatters.common import telegram_user_hmention


def amount_enter(part_participant: Dict, **kwargs) -> str:
    """Get text for entering part amount."""
    return fmt.text(
        fmt.text('Введите сумму для'),
        telegram_user_hmention(part_participant['first_name'], part_participant['user_id']),
    )


def amounts(part_amounts: Dict, **kwargs) -> str:
    """Get text for part amounts."""
    texts = []

    for part_amount in part_amounts:
        part_amount['amount'] = str(part_amount['amount']).rstrip('.0')

        text = fmt.text(
            telegram_user_hmention(part_amount['first_name'], part_amount['user_id']),
            fmt.text(': {amount}'),
            sep='',
        ).format(**part_amount)

        texts.append(text)

    return fmt.text(*texts, sep='\n')


def amounts_already_entered(part_amounts: Dict, **kwargs) -> str:
    """Get text for already entered part amounts."""
    part_amounts_text = amounts(part_amounts)

    text = fmt.text(
        fmt.text('Уже введенные доли'),
        part_amounts_text,
        sep='\n',
    )

    return '<i>{}</i>'.format(text)
