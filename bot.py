from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

storage = MemoryStorage()
bot = Bot(token='5786564151:AAFIfC7TMYCpsALlSP7Y9WJDMnGda0P3td8')
dp = Dispatcher(bot, storage=storage)

member_id_username = dict()
member_username_id = dict()


class FSMprocess(StatesGroup):
    ban_user = State()
    unban_user = State()
    new_admin = State()
    set_photo = State()


async def check_root(message: types.Message):
    for admin in (await bot.get_chat_administrators(chat_id=message.chat.id)):
        if admin["user"]["id"] == message.from_user.id:
            return True
    return False


async def update(message: types.Message):
    member_username_id.setdefault(message.chat.id, dict())
    member_id_username.setdefault(message.chat.id, dict())

    member_id_username[message.chat.id][
        message.from_user.id] = '@' + message.from_user.username if message.from_user.username is not None else ''
    member_username_id[message.chat.id][
        '@' + message.from_user.username if message.from_user.username is not None else ''] = message.from_user.id

    for member in message.new_chat_members:
        member_username_id.setdefault(message.chat.id, dict())
        member_id_username.setdefault(message.chat.id, dict())

        member_id_username[message.chat.id][member.id] = '@' + member.username if member.username is not None else ''
        member_username_id[message.chat.id]['@' + member.username if member.username is not None else ''] = member.id


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if message.from_user.id != message.chat.id:
        await set_default_commands()
        if await check_root(message):
            await message.answer("Бот развернут")
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def some_handler(message: types.Message):
    if message.from_user.id != message.chat.id:
        await message.answer("Привет я бот-менеджер чата, расскажешь нам о себе?)")
        await update(message)
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="get_members")
async def get_stat(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await message.answer(
                f"Количество администраторов: {len(await bot.get_chat_administrators(chat_id=message.chat.id))}\n"
                f"Количество членов чата(без меня): {await bot.get_chat_member_count(chat_id=message.chat.id) - 1}\n")
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="kick_bot")
async def leave_chat(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await message.answer("Всем пока!")
            await bot.leave_chat(chat_id=message.chat.id)
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="ban")
async def get_user_id_for_unban(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await FSMprocess.ban_user.set()
            await message.answer("Введите его имя пользователя, начинающееся на @")
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(state=FSMprocess.ban_user)
async def ban_user(message: types.Message, state: FSMContext):
    if message.from_user.id != message.chat.id:
        if message.text.strip(' ')[0] != '@':
            await message.reply('Неверный формат ввода username')
        else:
            try:
                await bot.ban_chat_member(chat_id=message.chat.id,
                                          user_id=int(member_username_id[message.chat.id][message.text.strip(' ')]))
                await message.answer("Пользователь забанен")
            except KeyError:
                await message.reply(
                    'Пользователя с таким username нет в чате либо он вступил в чат раньше меня и с того момента, как я пришел не написал ни одного сообщения')
        await state.finish()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="unban")
async def get_user_id_for_ban(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await FSMprocess.unban_user.set()
            await message.answer("Введите его имя пользователя, начинающееся на @")
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(state=FSMprocess.unban_user)
async def unban_user(message: types.Message, state: FSMContext):
    if message.from_user.id != message.chat.id:
        if message.text.strip(' ')[0] != '@':
            await message.reply('Неверный формат ввода username')
        else:
            try:
                await bot.unban_chat_member(chat_id=message.chat.id,
                                            user_id=int(member_username_id[message.chat.id][message.text.strip(' ')]))
                await message.answer("Пользователь разбанен")
            except KeyError:
                await message.reply(
                    'Пользователя с таким username нет в чате либо он вступил в чат раньше меня и с того момента, как я пришел не написал ни одного сообщения')
        await state.finish()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="set_admin")
async def set_admin1(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await FSMprocess.new_admin.set()
            await message.answer("Введите его имя пользователя, начинающееся на @")
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(state=FSMprocess.new_admin)
async def set_admin2(message: types.Message, state: FSMContext):
    if message.from_user.id != message.chat.id:
        if message.text.strip(' ')[0] != '@':
            await message.reply('Неверный формат ввода username')
        else:
            try:
                await bot.promote_chat_member(chat_id=message.chat.id,
                                              user_id=int(member_username_id[message.chat.id][message.text.strip(' ')]),
                                              can_manage_chat=True,
                                              can_change_info=True,
                                              can_delete_messages=True,
                                              can_manage_video_chats=True,
                                              can_promote_members=True,
                                              can_pin_messages=True,
                                              can_edit_messages=True,
                                              can_post_messages=True,
                                              can_restrict_members=True,
                                              can_invite_users=True)
                await message.answer("Администратор добавлен")
            except KeyError:
                await message.reply(
                    'Пользователя с таким username нет в чате либо он вступил в чат раньше меня и с того момента, как я пришел не написал ни одного сообщения')

        await state.finish()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="pin")
async def pin(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            try:
                await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
            except:
                await message.answer('Напишите /pin в виде ответа на сообщение, которое хотите закрепить')
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="unpin")
async def unpin(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            try:
                await bot.unpin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
            except:
                await message.answer('Напишите /unpin в виде ответа на сообщение, которое хотите открепить')
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="unpin_all")
async def unpin_all(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            try:
                await bot.unpin_all_chat_messages(chat_id=message.chat.id)
            except:
                await message.answer('Нет закрепленных сообщений')
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="set_photo")
async def set_photo1(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await FSMprocess.set_photo.set()
            await message.answer(
                'Пришлите фото, которое хотели бы поставить на чат.\nЕсли не желаете устанавливать фото, напишите "Отмена"')
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(content_types=['photo'], state=FSMprocess.set_photo)
async def set_photo2(message, state: FSMContext):
    if message.from_user.id != message.chat.id:
        try:
            await message.photo[-1].download('test.jpg')
            await bot.set_chat_photo(message.chat.id, InputFile('test.jpg'))
            await state.finish()
        except:
            await message.answer(
                'Фото чересчур маленькое, пришлите мне другое фото.\nЕсли не желаете устанавливать фото, напишите "Отмена"')
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(state=FSMprocess.set_photo)
async def set_photo2(message, state: FSMContext):
    if message.from_user.id != message.chat.id:
        if 'отмена' == message.text.strip(' ').lower():
            await message.reply('Процесс завершен')
            await state.finish()
        else:
            await message.answer(
                'Неверный формат ввода. Пришлите мне фото.\nЕсли не желаете устанавливать фото, напишите "Отмена"')
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="del_photo")
async def del_photo(message: types.Message):
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            await bot.delete_chat_photo(chat_id=message.chat.id)
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')



@dp.message_handler(commands='ping_all')
async def ping_all(message: types.Message):
    if message.from_user.id != message.chat.id:
        try:
            ls = member_username_id[message.chat.id]
            print(' '.join(ls))
            await message.answer(' '.join(ls))
        except:
            await message.answer('Нас двое, пинговать некого!')
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')

info = '''
<b>Descriprion of commands:</b>
<u>start</u>       - Запустить бота
<u>get_members</u> - Узнать количество администраторов и участников чата
<u>kick_bot</u>    - Выйти ботом из чата
<u>ban</u>         - Забанить(удалить из чата и внести в черный список) какого-то участника по username
<u>unban</u>       - Разбанить(удалить из черного списка) какого-то участника по username
<u>set_admin</u>   - Выдать админку какому-то участнику по username
<u>set_photo</u>   - Уcтановить фото на чат
<u>del_photo</u>   - Удалить текущее фото чата
<u>ping_all</u>    - Пинганет всех участников
<u>pin</u>         - Закрепить сообщение(используйте ее в виде ответа на сообщение, которое хотите закрепить)
<u>unpin</u>       - Открепить сообщение(используйте ее в виде ответа на сообщение, которое хотите открепить)
<u>unpin_all</u>   - Открепить все закрепленные сообщения
'''


@dp.message_handler(commands='help')
async def ping_all(message: types.Message):
    try:
        await bot.send_message(chat_id=message.from_user.id, text=info, parse_mode="HTML")
    except:
        await message.reply('Запусти бота, чтобы он ответил тебе в личку')


async def set_default_commands():
    await bot.set_my_commands(commands=[
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Бот направит в личку информацию по командам>"),
        types.BotCommand("get_members", "Узнать количество администраторов и участников чата"),
        types.BotCommand("kick_bot", "Выйти ботом из чата"),
        types.BotCommand("ban", "Забанить(удалить из чата и внести в черный список) какого-то участника по username"),
        types.BotCommand("unban", "Разбанить(удалить из черного списка) какого-то участника по username"),
        types.BotCommand("set_admin", "Выдать админку какому-то участнику по username"),
        types.BotCommand("set_photo", "Уcтановить фото на чат"),
        types.BotCommand("del_photo", "Удалить текущее фото чата"),
        types.BotCommand("ping_all", "Пинганет всех участников"),
        types.BotCommand("pin",
                         "Закрепить сообщение(используйте ее в виде ответа на сообщение, которое хотите закрепить)"),
        types.BotCommand("unpin",
                         "Открепить сообщение(используйте ее в виде ответа на сообщение, которое хотите открепить)"),
        types.BotCommand("unpin_all",
                         "Открепить все закрепленные сообщения"),

    ])


@dp.message_handler()
async def last(message: types.Message):
    if message.from_user.id != message.chat.id:
        await update(message)
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


executor.start_polling(dp, skip_updates=True)
