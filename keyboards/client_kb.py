from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           KeyboardButton)

from keyboards.utils_kb import back_button


request_button = InlineKeyboardButton('📛 Оставить заявку',
                                      callback_data='client_menu_request')
contact_button = InlineKeyboardButton('📞 Связаться', callback_data='client_menu_contact')
setting_button = InlineKeyboardButton('⚙ Настройки', callback_data='client_menu_profile')
contact_list_button = InlineKeyboardButton('☎ Полезные контакты',
                                           callback_data='client_menu_contact_list')

menu_kb = InlineKeyboardMarkup().row(request_button, contact_button).row(setting_button).row(contact_list_button)


back_menu_button = back_button('client_back_menu')
change_name_button = InlineKeyboardButton('🛠 Поменять имя', callback_data='profile_name')
change_phone_button = InlineKeyboardButton('🛠 Поменять номер', callback_data='profile_phone')

profile_kb = InlineKeyboardMarkup().row(change_name_button, change_phone_button).row(back_menu_button)


appeal_button = InlineKeyboardButton('📛 Оставить заявку', callback_data='request_appeal')
suggestion_button = InlineKeyboardButton('💡 Оставить предложение', callback_data='request_suggestion')

request_menu = InlineKeyboardMarkup().row(appeal_button, suggestion_button).row(back_menu_button)


contact_phone_button = InlineKeyboardButton('📞 Перезвоните мне', callback_data='contact_phone')
contact_bot_button = InlineKeyboardButton('📞 Свяжитесь со мной в чат-боте', callback_data='contact_bot')

contact_menu = InlineKeyboardMarkup(
    row_width=1
).add(contact_phone_button, contact_bot_button, back_menu_button)


contact_phone_yes_button = InlineKeyboardButton('✅ Да', callback_data='contact_phone_yes')
back_contact_menu_button = back_button('client_back_contact')

contact_phone_menu = InlineKeyboardMarkup().add(contact_phone_yes_button, back_contact_menu_button)


back_request_button = back_button('client_back_request')

back_appeal_address_button = back_button('client_back_appeal_address')

back_appeal_photo_button = back_button('client_back_appeal_photo')

skip_button = InlineKeyboardButton('▶ Пропустить', callback_data='skip_step')

appeal_photo_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('▶ Вперед'), KeyboardButton('🔙 Назад'))


