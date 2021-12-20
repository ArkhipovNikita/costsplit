import aiogram.utils.markdown as fmt

from src.models import Trip


def trip_base_fmt(trip: Trip) -> str:
    parts = [fmt.text('Путешествие')]

    if trip.name:
        parts.append(fmt.text('«{}»'.format(trip.name)))

    parts.append(fmt.text('началось ✈️'))

    return fmt.text(*parts, sep=' ')


def trip_already_started_fmt() -> str:
    return fmt.text(
        fmt.text('Вы уже в путешествии 🙌'),
        fmt.text('Для начала нового – завершите текущее.'),
        sep='\n'
    )
