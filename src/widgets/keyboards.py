import itertools
import operator
from typing import Any
from typing import Callable as CallableType
from typing import Dict, List, Optional, Sequence, Union

from aiogram.types import InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Column, Group, Keyboard
from aiogram_dialog.widgets.kbd.select import ItemIdGetter, get_identity
from aiogram_dialog.widgets.text import Format, Text
from aiogram_dialog.widgets.when import WhenCondition

from src import formatters as fmt
from src.widgets.texts import Callable


class Zipped(Group):
    """Class to zip several `Column` keyboards into «table»."""

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


class ListURL(Keyboard):
    """Class to render list of link buttons."""

    def __init__(
            self,
            text: Text,
            url: Text,
            items: Union[str, Sequence],
            id: Optional[str] = None,
            when: Union[str, CallableType, None] = None,
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


class ListUserURL(ListURL):
    """Class to render list of link buttons to users."""

    def __init__(
            self,
            user_id_getter: ItemIdGetter,
            items: Union[str, Sequence],
            text: Optional[str] = None,
            id: Optional[str] = None,
            when: Union[str, CallableType, None] = None,
    ):
        text = text or Format(fmt.consts.LINK_SYMBOL)
        url = Callable(
            lambda data, item, pos, pos0: fmt.common.telegram_user_url(
                user_id_getter(item)
            )
        )

        super().__init__(
            text=text,
            url=url,
            items=items,
            id=id,
            when=when,
        )
