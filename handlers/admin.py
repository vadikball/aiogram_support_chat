
import traceback
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

from create_bot import bot, send_message_to_other
from data_base.engine import (proceed_session,
                              get_user_active,
                              create_user,
                              change_user_admin,
                              get_user_phone,
                              get_active_users_id,
                              get_users_filter_active,
                              get_user_with_query,
                              get_all_users,
                              select,
                              session)
from data_base.models import User

from bot_texts import AdminTexts
from keyboards import admin_kb
from utils.state import state_maker
from settings import (StateSettings,
                      phone_number_sequence,
                      tg_user_name_sequence,
                      ru_user_name_sequence)
from utils.paginator import (paginator_cash,
                             create_paginator,
                             finish_paginator)

state_settings = StateSettings()


class FSMAdminMix(StatesGroup):
    """
    mass_send для рассылки ообщения пользователям
    active для редактирования черного списка
    """
    mass_send = State()

    active = State()

    search = State()

    admin_dialog = State()


async def get_admins(admin_chat_id) -> tuple[Any]:
    admins = await bot.get_chat_administrators(admin_chat_id)
    return tuple(admin.user.id for admin in admins)


async def send_admin_menu(chat_id):
    await bot.send_message(
        chat_id,
        AdminTexts.admin_menu,
        reply_markup=admin_kb.admin_menu_kb
    )


async def admin_back_to(callback: types.CallbackQuery):
    if callback.data.endswith('_menu'):
        await callback.message.edit_text(
            AdminTexts.admin_menu,
            reply_markup=admin_kb.admin_menu_kb
        )
    elif callback.data.endswith('_black_list'):
        await finish_paginator(callback.from_user.id)

        await bot.send_message(
            callback.from_user.id,
            AdminTexts.black_list_menu,
            reply_markup=admin_kb.black_list_menu
        )
    elif callback.data.endswith('_users_info'):
        await finish_paginator(callback.from_user.id)

        await bot.send_message(
            callback.from_user.id,
            AdminTexts.users_info_menu,
            reply_markup=admin_kb.users_info_menu
        )


async def start_chat_resolver(callback: types.CallbackQuery):
    state_maker(proxy='admin_dialog.json').set_state({
        callback.from_user.id: int(callback.data.split('#')[1]),
        callback.data.split('#')[1]: callback.from_user.id
    })

    await callback.message.delete()
    await callback.message.answer(
        AdminTexts.start_chat_admin,
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌📞 Завершить диалог'))
    )

    await FSMAdminMix.admin_dialog.set()


async def send_message_to_user(message: types.Message, state: FSMContext):
    if message.text.lower().endswith('завершить диалог'):
        user_id = state_maker(proxy='admin_dialog.json').get_key(str(message.from_user.id))
        await send_message_to_other(user_id, AdminTexts.cancel_chat_admin)
        state_maker(proxy='admin_dialog.json').del_pairs(message.from_user.id)

        await bot.send_message(
            message.from_user.id,
            AdminTexts.cancel_chat_admin,
            reply_markup=ReplyKeyboardRemove()
        )
        await state.finish()

    else:
        user_id = state_maker(proxy='admin_dialog.json').get_key(str(message.from_user.id))
        if user_id is None:
            await state.finish()
        await send_message_to_other(user_id, message.text)


async def paginator_stepper(callback: types.CallbackQuery):
    if callback.data.startswith('next'):
        await paginator_cash.get(callback.from_user.id).next_page()
    elif callback.data.startswith('previous'):
        await paginator_cash.get(callback.from_user.id).previous_page()


async def paginator_resolver(callback: types.CallbackQuery):
    paginator = paginator_cash.get(callback.from_user.id)
    user: User = paginator.get(callback.data.split('#')[1])

    await proceed_session(change_user_admin, user_id=user.user_id, key='active', value=not user.active)

    await paginator.finish()

    await bot.send_message(
        callback.from_user.id,
        AdminTexts.paginator_success
    )


async def users_list_resolver(callback: types.CallbackQuery):
    await callback.message.delete()
    if callback.data.endswith('_list'):
        users = await get_all_users(session)
        paginator = create_paginator(callback.from_user.id, users, admin_kb.back_users_list_button, False)
        await paginator.start()
    elif callback.data.endswith('_search'):
        await FSMAdminMix.search.set()
        await bot.send_message(
            callback.from_user.id,
            AdminTexts.users_list_search
        )


async def search_user(message: types.Message, state: FSMContext):
    query = None

    if re.match(phone_number_sequence, message.text):
        query = select(User).where(User.phone_number == message.text)
    elif re.match(tg_user_name_sequence, message.text):
        query = select(User).where(User.tg_user_name == message.text)
    elif re.match(ru_user_name_sequence, message.text):
        query = select(User).where(User.name == message.text)
    else:
        if len(message.text) < 33:
            try:
                search_data = int(message.text)
            except ValueError:
                pass
            else:
                query = select(User).where(User.user_id == search_data)

    if query is not None:
        user: Optional[User] = await get_user_with_query(session, query)
        if user is not None:
            await message.answer(
                str(user)
            )
        else:
            await message.answer(
                AdminTexts.search_failed
            )

    await state.finish()


async def black_list_resolver(callback: types.CallbackQuery):
    await callback.message.delete()
    users = tuple()
    if callback.data.endswith('_ban'):
        users = await get_users_filter_active(session, active=True)

    elif callback.data.endswith('_unban'):
        users = await get_users_filter_active(session, active=False)

    paginator = create_paginator(callback.from_user.id, users, admin_kb.back_black_list_button)
    await paginator.start()


async def admin_menu_resolver(callback: types.CallbackQuery):
    if callback.data.endswith('mass_send'):
        await FSMAdminMix.mass_send.set()
        await callback.message.edit_text(
            AdminTexts.mass_send_menu,
            reply_markup=InlineKeyboardMarkup().add(admin_kb.back_admin_menu_button)
        )
    elif callback.data.endswith('black_list'):
        await callback.message.edit_text(
            AdminTexts.black_list_menu,
            reply_markup=admin_kb.black_list_menu
        )
    elif callback.data.endswith('users_info'):
        await callback.message.edit_text(
            AdminTexts.users_info_menu,
            reply_markup=admin_kb.users_info_menu
        )


async def make_mass_send(message: types.Message, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message_id - 1)
    if message.text is not None:
        await state.finish()

        users = await proceed_session(get_active_users_id)
        for user_id in users:
            try:
                await bot.send_message(
                    user_id,
                    message.text
                )
            finally:
                continue

        await bot.send_message(
            message.from_user.id,
            AdminTexts.mass_send_success
        )
    else:
        await bot.send_message(
            message.from_user.id,
            AdminTexts.mass_send_failed,
            reply_markup=InlineKeyboardMarkup().add(admin_kb.back_admin_menu_button)
        )


async def admin_menu(message: types.Message):
    admin_chat_id = state_maker().get_key(state_settings.main_admin_chat)
    admins = await get_admins(admin_chat_id)

    if message.from_user.id in admins:
        await send_admin_menu(message.from_user.id)


async def validate_chat_resolver(callback: types.CallbackQuery):
    if callback.data.endswith('_main_admin'):
        await callback.message.edit_text(
            AdminTexts.main_chat_valid
        )
        state_maker().set_state({
            state_settings.main_admin_chat: callback.message.chat.id
        })
    elif callback.data.endswith('_appeal_chat'):
        await callback.message.edit_text(
            AdminTexts.appeal_chat_valid
        )
        state_maker().set_state({
            state_settings.appeal_chat: callback.message.chat.id
        })
    elif callback.data.endswith('_suggestion_chat'):
        await callback.message.edit_text(
            AdminTexts.suggestion_chat_valid
        )
        state_maker().set_state({
            state_settings.suggestion_chat: callback.message.chat.id
        })


async def validate_chat(message: types.Message):
    if message.chat.type == 'group':
        main_admin_chat = state_maker().get_key(state_settings.main_admin_chat)
        if main_admin_chat is None:
            await message.answer(
                AdminTexts.validation_chat_choice,
                reply_markup=InlineKeyboardMarkup().add(admin_kb.main_admin_chat_button)
            )
        else:
            admins = await get_admins(main_admin_chat)
            if message.from_user.id in admins:
                if message.chat.id != main_admin_chat:
                    await message.answer(
                        AdminTexts.validation_chat_choice,
                        reply_markup=InlineKeyboardMarkup(row_width=1).add(
                            admin_kb.appeal_chat_button, admin_kb.suggestion_chat_button
                        )
                    )
        await message.delete()
    elif message.chat.type == 'private':
        await bot.send_message(
            message.from_user.id,
            AdminTexts.non_valid_chat
        )


async def clear_chats(message: types.Message):
    await message.delete()
    if message.chat.id == state_maker().get_key('main_admin_chat'):
        state_maker().clear_state()
        await message.answer(
            AdminTexts.cleared_admin_chats
        )


def register_handlers_admin(dp: Dispatcher):

    # dp.register_callback_query_handler(skip_step, Text(equals='skip_step'), state='*')
    dp.register_callback_query_handler(admin_back_to, Text(startswith='admin_back_'))
    dp.register_callback_query_handler(start_chat_resolver, Text(startswith='start_chat'))
    dp.register_callback_query_handler(paginator_resolver, Text(startswith='result'))
    dp.register_callback_query_handler(paginator_stepper, Text(endswith='_page'))
    dp.register_callback_query_handler(users_list_resolver, Text(startswith='users_info_'))
    dp.register_callback_query_handler(black_list_resolver, Text(startswith='black_list_'))
    dp.register_callback_query_handler(validate_chat_resolver, Text(startswith='validate_chat_'))
    dp.register_callback_query_handler(admin_menu_resolver, Text(startswith='admin_menu_'))

    dp.register_message_handler(admin_menu, commands=['admin', 'админ'])
    dp.register_message_handler(validate_chat, commands=['adminchat', 'админчат'])
    dp.register_message_handler(clear_chats, commands=['clearadminchats', 'удалитьадминчаты'])
    dp.register_message_handler(make_mass_send, state=FSMAdminMix.mass_send)
    dp.register_message_handler(search_user, state=FSMAdminMix.search)
    dp.register_message_handler(send_message_to_user, state=FSMAdminMix.admin_dialog)
    # dp.register_message_handler(change_phone, state=FSMChangeUser.phone_number)
    # dp.register_message_handler(suggestion_finish, state=FSMMix.suggestion_description)
    # dp.register_message_handler(appeal_address, state=FSMAppeal.address)
    # dp.register_message_handler(appeal_photo, state=FSMAppeal.photo)
    # dp.register_message_handler(appeal_description, state=FSMAppeal.description)
    # dp.register_message_handler(renew_user_phone_for_call_back, state=FSMMix.renew_user_phone)
    # dp.register_message_handler(send_message_to_admin, state=FSMMix.admin_dialog)
