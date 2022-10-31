# aiogram_support_chat

Чат бот службы поддержки с динамически обновляемыми сообщениями, с кастомной пагинацией.

Выполненно на aiogram, sqlalchemy, aiosqlite

Для инициализации бота необходимо поместить файл .env в корень репозитория с ключами
TOKEN - токен доступа телеграм бота
DB_STR - строка подключения к бд

Например: 

    sqlite+aiosqlite:///database.db
    
    или
    
    postgresql+asyncpg://<db_username>:<db_secret>@<db_host>:<db_port>/<db_name>

