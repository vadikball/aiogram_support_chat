
import re
from typing import Optional, Any

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (InlineKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot_texts import ClientTexts
from create_bot import bot, delete_previous_message, send_message_to_other
from data_base.engine import (proceed_session,
                              get_user_active,
                              create_user,
                              change_user,
                              get_user_phone,
                              get_user)
from data_base.models import User
from keyboards import client_kb
from keyboards.utils_kb import start_chat_kb
from settings import phone_number_sequence, StateSettings
from utils.state import state_maker


state_settings = StateSettings()
class FSMChangeUser(StatesGroup):
    name = State()
    phone_number = State()


class FSMCreateUser(StatesGroup):
    name = State()
    phone_number = State()


class FSMAppeal(StatesGroup):
    address = State()
    photo = State()
    description = State()


class FSMMix(StatesGroup):
    """ микс одношаговых стэйтов"""
    suggestion_description = State()

    renew_user_phone = State()
    admin_dialog = State()


async def load_user_admin_chat(user_id) -> tuple[Any, str, dict]:
    user: dict = await proceed_session(get_user, user_id=user_id)
    main_admin_chat = state_maker().get_key('main_admin_chat')

    print(user)

    user_info = '{0}\n{1}\ntg: {2}\n'.format(
        user['name'], user['phone_number'], user['tg_user_name']
    ) if user['tg_user_name'] is not None else '{0}\n{1}\n'.format(user['name'], user['phone_number'])

    return main_admin_chat, user_info, user


async def send_request(message: types.Message, data: Optional[dict], chat: str):
    """ Отправляет запрос в админский чат """
    user_info = (await load_user_admin_chat(message.from_user.id))[1]
    admin_chat_id = state_maker().get_key(chat)

    if admin_chat_id is None:
        main_admin_chat = state_maker().get_key('main_admin_chat')
        if main_admin_chat is not None:
            await bot.send_message(
                main_admin_chat,
                ClientTexts.request_chat_not_found
            )
            admin_chat_id = main_admin_chat

    if admin_chat_id is not None:
        if data.get('address'):
            message_text = '{0}\n{1}\n Адрес:{2}'.format(
                user_info, data.get('description'), data.get('address')
            )
        else:
            message_text = '{0}\n{1}'.format(
                user_info, data.get('description')
            )

        if data.get('video'):
            await bot.send_video(
                admin_chat_id,
                data.get('video')
            )

        photos = data.get('photo')
        if photos:
            for photo in photos:
                await bot.send_photo(
                    admin_chat_id,
                    photo
                )

        await bot.send_message(
            admin_chat_id,
            message_text
        )


async def send_ring_up_request(user_id):
    """ Отправляет запрос об обратном звонке в чат админов """
    main_admin_chat, user_info, _ = await load_user_admin_chat(user_id)

    if main_admin_chat is not None:
        await bot.send_message(
            main_admin_chat,
            '{0}{1}'.format(user_info, ClientTexts.request_for_call_back)
        )


async def notify_admin_chat(user_id):
    """ Отправляет сообщение в админский чат с просьбой диалога через бота """
    main_admin_chat, user_info, _ = await load_user_admin_chat(user_id)

    if main_admin_chat is not None:
        await bot.send_message(
            main_admin_chat,
            '{0}{1}'.format(user_info, ClientTexts.request_for_admin_dialog),
            reply_markup=start_chat_kb(user_id)
        )


async def send_menu(chat_id):
    """ Отправляет главное меню """
    await bot.send_message(
        chat_id,
        ClientTexts.start_command_true,
        reply_markup=client_kb.menu_kb
    )


async def request_menu(callback: types.CallbackQuery):
    """ Отправляет меню запросов """
    await callback.message.edit_text(
        ClientTexts.request,
        reply_markup=client_kb.request_menu
    )


async def contact_menu(callback: types.CallbackQuery):
    """ Отправляет меню контакта """
    await callback.message.edit_text(
        ClientTexts.contact,
        reply_markup=client_kb.contact_menu
    )


async def skip_step(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await FSMAppeal.next()
        if callback.message.text == ClientTexts.appeal_address:
            await callback.message.delete()
            await bot.send_message(
                callback.message.chat.id,
                ClientTexts.appeal_photo,
                reply_markup=client_kb.appeal_photo_kb
            )


async def back_to(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

    if callback.data.endswith('menu'):
        await callback.message.edit_text(
            ClientTexts.start_command_true,
            reply_markup=client_kb.menu_kb
        )
    elif callback.data.endswith('request'):
        await request_menu(callback)
    elif callback.data.endswith('appeal_address'):
        await FSMAppeal.address.set()
        await callback.message.edit_text(
            ClientTexts.appeal_address,
            reply_markup=InlineKeyboardMarkup().add(client_kb.skip_button).row(client_kb.back_request_button)
        )
    elif callback.data.endswith('appeal_photo'):
        await FSMAppeal.photo.set()
        await callback.message.delete()
        await bot.send_message(
            callback.message.chat.id,
            ClientTexts.appeal_photo,
            reply_markup=client_kb.appeal_photo_kb
        )
    elif callback.data.endswith('contact'):
        await contact_menu(callback)


async def contact_resolver(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.endswith('phone'):
        phone_number = await proceed_session(get_user_phone, user_id=callback.message.chat.id)
        await callback.message.edit_text(
            '{0} {1}'.format(phone_number, ClientTexts.contact_phone_menu),
            reply_markup=client_kb.contact_phone_menu
        )
        await FSMMix.renew_user_phone.set()
    elif callback.data.endswith('phone_yes'):
        await send_ring_up_request(callback.from_user.id)
        await state.finish()
        await callback.message.edit_text(
            ClientTexts.contact_phone_yes,
        )
        await send_menu(callback.message.chat.id)
    elif callback.data.endswith('bot'):
        await callback.message.delete()
        await bot.send_message(
            callback.from_user.id,
            ClientTexts.contact_bot_admin,
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌📞 Завершить диалог'))
        )
        await notify_admin_chat(callback.from_user.id)
        await FSMMix.admin_dialog.set()


async def send_message_to_admin(message: types.Message, state: FSMContext):
    if message.text.lower().endswith('завершить диалог'):
        admin_id = state_maker(proxy=state_settings.admin_dialog_json).get_key(str(message.from_user.id))
        user = await proceed_session(get_user, user_id=message.from_user.id)
        message_text = '{0}\n{1}\n{2}\n{3}'.format(
            user['tg_user_name'],
            user['name'],
            user['phone_number'],
            ClientTexts.contact_bot_admin_cancel
        )
        await send_message_to_other(admin_id, message_text)

        state_maker(proxy=state_settings.admin_dialog_json).del_pairs(str(message.from_user.id))

        await bot.send_message(
            message.from_user.id,
            ClientTexts.contact_bot_admin_cancel,
            reply_markup=ReplyKeyboardRemove()
        )
        await state.finish()
        await send_menu(message.from_user.id)
    else:
        admin_id = state_maker(proxy=state_settings.admin_dialog_json).get_key(str(message.from_user.id))
        if admin_id is None:
            await state.finish()

        user = await proceed_session(get_user, user_id=message.from_user.id)
        message_text = '{0}\n{1}\n{2}\n{3}'.format(
            user['tg_user_name'],
            user['name'],
            user['phone_number'],
            message.text
        )
        await send_message_to_other(admin_id, message_text)
        await send_message_to_other(admin_id, message.text)


async def renew_user_phone_for_call_back(message: types.Message, state: FSMContext):
    await delete_previous_message(message)
    if re.match(phone_number_sequence, message.text):
        await proceed_session(change_user, message=message, key='phone_number')
        await bot.send_message(
            message.from_user.id,
            ClientTexts.contact_phone_yes
        )
        await send_ring_up_request(message.from_user.id)
        await state.finish()
        await send_menu(message.chat.id)
    else:
        phone_number = await proceed_session(get_user_phone, user_id=message.chat.id)
        await bot.send_message(
            message.from_user.id,
            '{0} {1}'.format(phone_number, ClientTexts.contact_phone_renew_failed),
            reply_markup=client_kb.contact_phone_menu
        )


async def request_resolver(callback: types.CallbackQuery):
    if callback.data.endswith('appeal'):
        await FSMAppeal.address.set()
        await callback.message.edit_text(
            ClientTexts.appeal_address,
            reply_markup=InlineKeyboardMarkup().add(client_kb.skip_button).row(client_kb.back_request_button)
        )
    elif callback.data.endswith('suggestion'):
        await FSMMix.suggestion_description.set()
        await callback.message.edit_text(
            ClientTexts.suggestion_description,
            reply_markup=InlineKeyboardMarkup().add(client_kb.back_request_button)
        )


async def appeal_address(message: types.Message, state: FSMContext):
    await delete_previous_message(message)
    if message.text is not None:
        async with state.proxy() as data:
            data['address'] = message.text
        await FSMAppeal.next()
        await bot.send_message(
            message.from_user.id,
            ClientTexts.appeal_photo,
            reply_markup=client_kb.appeal_photo_kb
        )
    else:
        bot.send_message(
            message.from_user.id,
            ClientTexts.appeal_address_failed,
            reply_markup=InlineKeyboardMarkup().add(client_kb.skip_button).row(client_kb.back_request_button)
        )


async def appeal_photo(message: types.Message, state: FSMContext):
    if message.photo or message.video is not None:
        async with state.proxy() as data:
            if data.get('photo') is None:
                data['photo'] = [message.photo[0].file_id]
            else:
                data['photo'].append(message.photo[0].file_id)
            if message.video is not None:
                data['video'] = message.video.file_id

    else:
        if message.text.lower().endswith('назад'):
            await FSMAppeal.address.set()
            mes = await bot.send_message(
                message.chat.id,
                '*',
                reply_markup=ReplyKeyboardRemove()
            )
            await mes.delete()

            await bot.send_message(
                message.chat.id,
                ClientTexts.appeal_address,
                reply_markup=InlineKeyboardMarkup().add(client_kb.skip_button).row(
                    client_kb.back_request_button)
            )
        else:
            await FSMAppeal.next()

            await bot.send_message(
                message.from_user.id,
                ClientTexts.appeal_description,
                reply_markup=InlineKeyboardMarkup().add(client_kb.back_appeal_photo_button)
            )


async def appeal_description(message: types.Message, state: FSMContext):
    await delete_previous_message(message)
    if message.text is not None:
        async with state.proxy() as data:
            data['description'] = message.text
            await send_request(message, data, 'appeal_chat')
        await bot.send_message(
            message.from_user.id,
            ClientTexts.appeal_finish
        )
        await state.finish()
        await send_menu(message.from_user.id)
    else:
        await bot.send_message(
            message.from_user.id,
            ClientTexts.appeal_description_failed,
            reply_markup=InlineKeyboardMarkup().add(client_kb.back_appeal_photo_button)
        )


async def suggestion_finish(message: types.Message, state: FSMContext):
    await delete_previous_message(message)
    if message.text is None:
        await bot.send_message(
            message.from_user.id,
            ClientTexts.suggestion_description_failed
        )
    else:

        await bot.send_message(
            message.from_user.id,
            ClientTexts.suggestion_finish
        )

        await send_request(message, {'description': message.text}, 'suggestion_chat')
        await state.finish()
        await send_menu(message.from_user.id)


async def profile_resolver(callback: types.CallbackQuery):
    if callback.data.endswith('name'):
        await FSMChangeUser.name.set()
        await callback.message.edit_text(
            ClientTexts.profile_name
        )
    elif callback.data.endswith('phone'):
        await FSMChangeUser.phone_number.set()
        await callback.message.edit_text(
            ClientTexts.profile_phone
        )


async def change_name(message: types.Message, state: FSMContext):
    await proceed_session(change_user, message=message, key='name')
    await bot.send_message(
        message.from_user.id,
        ClientTexts.profile_name_success
    )
    await state.finish()
    await send_menu(message.chat.id)


async def change_phone(message: types.Message, state: FSMContext):
    if re.match(phone_number_sequence, message.text):
        await proceed_session(change_user, message=message, key='phone_number')
        await bot.send_message(
            message.from_user.id,
            ClientTexts.profile_phone_success
        )
        await state.finish()
        await send_menu(message.chat.id)
    else:
        await bot.send_message(
            message.from_user.id,
            ClientTexts.profile_phone_failed
        )


async def menu_resolver(callback: types.CallbackQuery):
    if callback.data.endswith('request'):
        await request_menu(callback)
    elif callback.data.endswith('contact'):
        await contact_menu(callback)
    elif callback.data.endswith('profile'):
        await callback.message.edit_text(
            ClientTexts.profile,
            reply_markup=client_kb.profile_kb
        )
    elif callback.data.endswith('contact_list'):
        await callback.message.edit_text(
            ClientTexts.contact_list
        )
        await send_menu(callback.from_user.id)


async def command_start(message: types.Message):

    is_active: Optional[bool] = await proceed_session(get_user_active, user_id=message.from_user.id)
    if is_active is None:
        await FSMCreateUser.name.set()
        await bot.send_message(
            message.from_user.id,
            ClientTexts.start_command_false_name
        )
    else:
        if is_active:
            try:
                await delete_previous_message(message)
            finally:
                await send_menu(message.from_user.id)


async def add_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMCreateUser.phone_number.set()
    await bot.send_message(
        message.from_user.id,
        ClientTexts.start_command_false_phone
    )


async def add_phone_number(message: types.Message, state: FSMContext):
    if re.match(phone_number_sequence, message.text):
        async with state.proxy() as data:
            user = User(
                user_id=message.from_user.id,
                name=data['name'],
                tg_user_name=message.from_user.username,
                phone_number=message.text,
                active=True
            )
        await proceed_session(create_user, user=user)
        await state.finish()
        await send_menu(message.from_user.id)
    else:
        await bot.send_message(
            message.from_user.id,
            ClientTexts.profile_phone_failed
        )


def register_handlers_client(dp: Dispatcher):

    dp.register_callback_query_handler(skip_step, Text(equals='skip_step'), state='*')
    dp.register_callback_query_handler(back_to, Text(startswith='client_back_'), state='*')
    dp.register_callback_query_handler(contact_resolver, Text(startswith='contact_'), state='*')
    dp.register_callback_query_handler(request_resolver, Text(startswith='request_'))
    dp.register_callback_query_handler(profile_resolver, Text(startswith='profile_'))
    dp.register_callback_query_handler(menu_resolver, Text(startswith='client_menu_'))

    dp.register_message_handler(command_start, commands=['start', 'help', 'меню', 'старт', 'помощь'])
    dp.register_message_handler(add_name, state=FSMCreateUser.name)
    dp.register_message_handler(add_phone_number, state=FSMCreateUser.phone_number)
    dp.register_message_handler(change_name, state=FSMChangeUser.name)
    dp.register_message_handler(change_phone, state=FSMChangeUser.phone_number)
    dp.register_message_handler(suggestion_finish, state=FSMMix.suggestion_description)
    dp.register_message_handler(appeal_address, state=FSMAppeal.address)
    dp.register_message_handler(appeal_description, state=FSMAppeal.description)
    dp.register_message_handler(renew_user_phone_for_call_back, state=FSMMix.renew_user_phone)
    dp.register_message_handler(send_message_to_admin, state=FSMMix.admin_dialog)
    dp.register_message_handler(appeal_photo, state=FSMAppeal.photo, content_types=['photo', 'video', 'text'])

