from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_button(callback_data: str):
    return InlineKeyboardButton('🔙 Назад', callback_data=callback_data)


def start_chat_kb(user_id: Union[str, int]):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Начать чат', callback_data='start_chat#{0}'.format(user_id))
    )
