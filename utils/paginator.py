

from typing import Union, Optional, Any

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bot


class Paginator:
    next_button = InlineKeyboardButton('Следующая страница', callback_data='next_page')
    previous_button = InlineKeyboardButton('Предыдущая страница', callback_data='previous_page')

    def __init__(self,
                 user_id: int,
                 data: Union[list, tuple],
                 back_kb: InlineKeyboardMarkup,
                 pointer: bool = True):
        self.user_id = user_id
        self.data = data
        self.back_kb = back_kb
        self.pointer = pointer
        self.current_page = 1
        self.pages = (len(data) // 10) + (1 if len(data) % 10 > 0 else 0)
        self.last_message_id = None

    def __str__(self):
        return 'Страница {0} из {1}'.format(
            self.current_page, self.pages
        ) if self.pages > 1 else '"Назад" - вернутся в предыдущее меню'

    def clear(self):
        del paginator_cash.data[self.user_id]

    async def delete_helper(self, message_count):
        for offset in range(message_count):
            await bot.delete_message(self.user_id, self.last_message_id - offset)

    async def delete_previous_messages(self):
        if self.data:
            if self.current_page != self.pages:
                await self.delete_helper(11)
            else:
                message_count = (len(self.data) % 10 if len(self.data) % 10 > 0 else 10) + 1
                await self.delete_helper(message_count)

    async def finish(self):
        await self.delete_previous_messages()
        self.clear()

    def get(self, index: Union[str, int]) -> Any:
        return self.data[int(index)]

    async def helper_send_rows(self, rows: Union[tuple, list]):
        for el in rows:
            await bot.send_message(
                self.user_id,
                str(el),
            )

    async def helper_send_rows_pointer(self, rows: Union[tuple, list], indexes: tuple[int]):
        for num, el in enumerate(rows):
            await bot.send_message(
                self.user_id,
                str(el),
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Выбрать', callback_data='result#{0}'.format(indexes[num]))
                )
            )

    async def next_page(self):
        if self.current_page + 1 <= self.pages:
            await self.delete_previous_messages()

            keyboard = InlineKeyboardMarkup()
            keyboard.add(self.previous_button)
            if self.current_page + 1 != self.pages:
                keyboard.add(self.next_button)
            keyboard.row(self.back_kb)

            await self.send_rows(self.current_page, self.current_page + 1)

            self.current_page += 1

            await self.send_keyboard(keyboard)

    async def previous_page(self):
        if self.current_page - 1 >= 1:
            await self.delete_previous_messages()

            keyboard = InlineKeyboardMarkup()

            if self.current_page - 1 != 1:
                keyboard.add(self.previous_button)
            keyboard.add(self.next_button)
            keyboard.row(self.back_kb)

            await self.send_rows(self.current_page - 2, self.current_page - 1)

            self.current_page -= 1

            await self.send_keyboard(keyboard)

    async def send_rows(self, from_: int = 0, to_: int = 1):
        rows = tuple(self.data[10 * from_:10 * to_])
        if self.pointer:
            indexes = tuple(self.data.index(_) for _ in rows)
            await self.helper_send_rows_pointer(rows, indexes)
        else:
            await self.helper_send_rows(rows)

    async def send_keyboard(self, keyboard: InlineKeyboardMarkup):
        mes = await bot.send_message(
            self.user_id,
            str(self),
            reply_markup=keyboard
        )
        self.last_message_id = mes.message_id

    async def start(self):
        keyboard = InlineKeyboardMarkup()
        if self.pages > 1:
            keyboard.add(self.next_button)
        keyboard.row(self.back_kb)

        await self.send_rows()

        await self.send_keyboard(keyboard)
        print(self.data)


class PaginatorCash:
    data = {}

    def get(self, chat_id: Union[str, int]) -> Optional[Paginator]:
        value = self.data.get(chat_id)
        if value is None:
            if isinstance(chat_id, int):
                value = self.data.get(str(chat_id))
            else:
                value = self.data.get(int(chat_id))
        return value

    def set(self, paginator: Paginator):
        self.data[paginator.user_id] = paginator


paginator_cash = PaginatorCash()


def create_paginator(user_id: int,
                     data: Union[list, tuple],
                     back_kb: InlineKeyboardMarkup,
                     pointer: bool = True) -> Optional[Paginator]:
    if data:
        paginator = Paginator(user_id, data, back_kb, pointer)
        paginator_cash.set(paginator)
        return paginator
    else:
        return None


async def finish_paginator(user_id: Union[str, int]):
    paginator = paginator_cash.get(user_id)
    if paginator is not None:
        await paginator.finish()

