from typing import Union

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from settings import Settings

settings = Settings()

storage = MemoryStorage()


bot = Bot(settings.token)
dp = Dispatcher(bot, storage=storage)


async def delete_previous_message(message: types.Message):
    for _ in range(10):
        try:
            await bot.delete_message(message.from_user.id, message.message_id - 1 - _)
            break
        except:
            continue


async def send_message_to_other(user_id: Union[str, int], text: str):
    if user_id is not None:
        await bot.send_message(
            user_id,
            text
        )
