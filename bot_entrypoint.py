import traceback

from aiogram.utils import executor

from create_bot import dp
from handlers import client, admin
from data_base.engine import proceed_schemas
# from data_base import sqlite_db


async def on_startup(_):
    print('Online...')
    await proceed_schemas()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
# other.register_handlers_other(dp)


if __name__ == '__main__':
    # while True:
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except:
        print(traceback.format_exc())

# client
# создание профайла клиента +
# главное меню + кнопки +
# редактирование профайла +
# назад и отмена хэндлер +
# полезные контакты +
# админские чаты +
# оставить заявку +
# связь по телефону +
# связь через бота +

# админ
# do state + validation +
# валидация админского чата +
# валидация чата категорий обращений +
# админское меню + кнопки +
# кнопки админ меню - рассылка, черный список, поиск пользователя +
# рассылка +
# черный список -> заблокировать/восстановить -> поиск пользователя по полю или список пользователей -> выбор пользователя и блок/актив +
# поиск пользователя по полю или списком +
# соединение юзера и админа +

