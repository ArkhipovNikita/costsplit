from typing import Callable as CallableType

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.when import WhenCondition


class Callable(Text):
    """Widget that calls a function to render text."""

    def __init__(self, func: CallableType[..., str], when: WhenCondition = None):
        super().__init__(when)
        self.func = func

    async def _render_text(self, data, manager: DialogManager) -> str:
        return self.func(**data)
