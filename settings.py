from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    db_str - Строка для подключения sqlalchemy к бд
    например:
    sqlite+aiosqlite:///database.db
    или
    postgresql+asyncpg://<db_username>:<db_secret>@<db_host>:<db_port>/<db_name>
    """
    token: str
    db_str: str

    class Config:
        env_file = '.env.sample', '.env'
        env_file_encoding = 'utf-8'


class StateSettings(BaseSettings):
    """ Инициализирует и хранит названия ключей для машины состояния """
    main_admin_chat: str = 'main_admin_chat'
    appeal_chat: str = 'appeal_chat'
    suggestion_chat: str = 'suggestion_chat'
    admin_dialog_json: str = 'admin_dialog.json'

    class Config:
        env_file = '.state.env.sample', '.state.env'
        env_file_encoding = 'utf-8'


phone_number_sequence = r'^\+7\d{10}$'
tg_user_name_sequence = r'^[a-z]*$'
ru_user_name_sequence = r'^[а-яА-Я]*\s[а-яА-Я]*$'
