
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton)

from keyboards.utils_kb import back_button

mass_send_button = InlineKeyboardButton('Рассылка', callback_data='admin_menu_mass_send')
black_list_button = InlineKeyboardButton('Черный список', callback_data='admin_menu_black_list')
users_info_button = InlineKeyboardButton('Информация о пользователях', callback_data='admin_menu_users_info')

admin_menu_kb = InlineKeyboardMarkup(
    row_width=1
).add(mass_send_button, black_list_button, users_info_button)

back_admin_menu_button = back_button('admin_back_menu')


bl_ban_button = InlineKeyboardButton('Внести в черный список', callback_data='black_list_ban')
bl_unban_button = InlineKeyboardButton('Удалить из черного списка', callback_data='black_list_unban')

black_list_menu = InlineKeyboardMarkup(row_width=1).add(bl_ban_button, bl_unban_button, back_admin_menu_button)


ui_list = InlineKeyboardButton('Показать список', callback_data='users_info_list')
ui_search = InlineKeyboardButton('Найти пользователя', callback_data='users_info_search')

users_info_menu = InlineKeyboardMarkup(row_width=1).add(ui_list, ui_search, back_admin_menu_button)


main_admin_chat_button = InlineKeyboardButton('🛠 Назначить текущий чат для админов',
                                              callback_data='validate_chat_main_admin')
appeal_chat_button = InlineKeyboardButton('📛 чат для заявок', callback_data='validate_chat_appeal_chat')
suggestion_chat_button = InlineKeyboardButton('💡 чат для предложения',
                                              callback_data='validate_chat_suggestion_chat')

back_black_list_button = back_button('admin_back_black_list')

back_users_list_button = back_button('admin_back_users_info')


start_chat_with_admin_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Начать чат', callback_data='start_chat'))
