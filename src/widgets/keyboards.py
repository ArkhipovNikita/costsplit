import itertools
import operator
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from aiogram.types import InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Column, Group, Keyboard
from aiogram_dialog.widgets.kbd.select import get_identity
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.when import WhenCondition


class Zipped(Group):
    """A class to zip several `Column` keyboards into «table»."""

    def __init__(self, *buttons: Column, id: Optional[str] = None, when: WhenCondition = None):
        super().__init__(*buttons, id=id, when=when, width=len(buttons))

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboards = [await button._render_keyboard(data, manager) for button in self.buttons]

        buttons = map(lambda keyboard: itertools.chain.from_iterable(keyboard), keyboards)
        zipped_keyboard: List[List[InlineKeyboardButton]] = list(map(list, zip(*buttons)))

        return zipped_keyboard


class Multiurl(Keyboard):
    """A class to render list of `Url` buttons using data from a getter."""

    def __init__(
            self,
            text: Text,
            url: Text,
            items: Union[str, Sequence],
            id: Optional[str] = None,
            when: Union[str, Callable, None] = None,
    ):
        super().__init__(id, when)

        self.text = text
        self.url = url

        if isinstance(items, str):
            self.items_getter = operator.itemgetter(items)
        else:
            self.items_getter = get_identity(items)

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [[
            await self._render_button(pos, item, data, manager)
            for pos, item in enumerate(self.items_getter(data))
        ]]

    async def _render_button(
            self,
            pos: int,
            item: Any,
            data: Dict,
            manager: DialogManager,
    ) -> InlineKeyboardButton:
        data = {'data': data, 'item': item, 'pos': pos + 1, 'pos0': pos}
        return InlineKeyboardButton(
            text=await self.text.render_text(data, manager),
            url=await self.url.render_text(data, manager),
        )
