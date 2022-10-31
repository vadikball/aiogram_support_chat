
from aiogram.utils import executor

from create_bot import dp
from handlers import client, admin
from data_base.engine import proceed_schemas


async def on_startup(_):
    print('Online...')
    await proceed_schemas()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)


if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



