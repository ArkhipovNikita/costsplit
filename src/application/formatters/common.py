from aiogram.utils import markdown as fmt


def telegram_user_url(user_id: int) -> str:
    """Get a link to a telegram user."""
    return 'tg://user?id={}'.format(user_id)


def telegram_user_mention(title: str, user_id: int) -> str:
    """Get a link to a telegram user (Markdown)."""
    telegram_user_url_ = telegram_user_url(user_id)
    return fmt.link(title, telegram_user_url_)


def telegram_user_hmention(title: str, user_id: int) -> str:
    """Get a link to a telegram user (HTML)."""
    telegram_user_url_ = telegram_user_url(user_id)
    return fmt.hlink(title, telegram_user_url_)
