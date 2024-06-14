from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import re
from datetime import datetime
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from FSM import Form
from keyboards import start_keyboard, enter_keyboard
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from API import API

API_TOKEN = '6051028622:AAHazo0jubESQ0PxLCYWGKtMVHKi5pV_1nM'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

scheduler = AsyncIOScheduler()
scheduler.start()

api = API()


async def scheduled_task():
    bithdays = api.check_happy_birthday()
    for bd in bithdays:
        subscribers = bd["subscribers"]
        for sub in subscribers:
            await bot.send_message(chat_id=int(sub["subscriber_id"]),
                             text=f"""У пользователя с ником {bd["name"]} сегодня день рождения!\nНе забудьте поздравить!""")
        await bot.send_message(chat_id=-1002208838775,
                                   text=f"""У пользователя с ником {bd["name"]} сегодня день рождения!\nНе забудьте поздравить!""")


scheduler.add_job(scheduled_task, "cron", hour=12, minute=29)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я бот помошник, который будет тебе напоминать о днях рождения!\n\nЧтобы начать, нажми кнопку авторизироваться ниже:",
        reply_markup=start_keyboard
    )



@dp.message_handler(commands=['subs'])
async def get_subs(message: types.Message):
    mes = "Ваши подписки:\n"
    users = api.get_employe_subs(int(message.from_user.id))
    for user in users:
        mes += str(user[0]) + "\n"

    if users == []:
        await bot.send_message(message.from_user.id, "Вы пока ни на кого не подписаны!")
    else:

        await bot.send_message(message.from_user.id, mes)


@dp.message_handler(lambda message: message.text == "авторизироваться!")
async def send_button_response(message: types.Message):
    users = api.get_all_users()
    if [message.from_user.username, int(message.from_user.id)] in users:
        await Form.registration_user.set()
        await message.answer("Вы уже авторизированы!\n\n"
                             "Нажмите /subs, чтобы получить ваши текущие подписки\n\n"
                             "Подпишитесь на группу, чтобы получать уведомления о др: https://t.me/+bgef6lPqCN8yN2Uy", reply_markup=enter_keyboard)
    else:
        await Form.waiting_for_date_of_birth.set()
        await message.reply("Напишите вашу дату рождения(в формате ДД.ММ.ГГГГ.): ", reply_markup=ReplyKeyboardRemove())


# Выражение для проверки формата ДД.ММ.ГГГГ
DATE_RE = re.compile(r'\b(\d{2})\.(\d{2})\.(\d{4})\b')


@dp.message_handler(regexp=DATE_RE, state=Form.waiting_for_date_of_birth)
async def handle_birthdate(message: types.Message, state: FSMContext):
    date_of_birth = "-".join([i for i in message.text.split(".")][::-1])
    username = message.from_user.username
    id = message.from_user.id

    print(date_of_birth, username, id)

    api.create_user(str(username), int(id), date_of_birth)

    try:
        birth_date = datetime.strptime(message.text, '%d.%m.%Y')
        await Form.registration_user.set()
        await message.reply(f"Ваша дата рождения {birth_date.strftime('%d.%m.%Y')} успешно сохранена!")
        await handle_registration_user(message, state)

    except ValueError:
        await message.reply("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")


@dp.message_handler(state=Form.registration_user)
async def handle_registration_user(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Поздравляю, вы успешно авторизировались!\n\n"
                         "Нажмите /subs, чтобы получить ваши текущие подписки\n\n"
                         "Подпишитесь на группу, чтобы получать уведомления о др:", reply_markup=enter_keyboard)


@dp.message_handler(
    lambda message: message.text in ["Подписаться на пользователя", "Отписаться от пользователя",
                                     "Подписаться на всех", "Отписаться от всех"])
async def get_subscription(message: types.Message, state: FSMContext):
    if message.text == "Подписаться на пользователя":

        subscribe_inline_keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

        subscriptions = api.get_employe_subs(int(message.from_user.id))
        users = api.get_all_users()
        users.remove([message.from_user.username, int(message.from_user.id)])
        for sub in subscriptions:
            users.remove(sub)
        for user in users:
            subscribe_inline_keyboard.add(types.InlineKeyboardButton(text=user[0], callback_data="sub-" + str(user[1])))

        if users == []:
            await message.reply("Вы подписаны уже на всех пользователей!")
        else:
            await message.reply("Выберете пользователя на которого хотите подписаться:",
                                reply_markup=subscribe_inline_keyboard)
    if message.text == "Отписаться от пользователя":
        unsubscribe_inline_keyboard = types.InlineKeyboardMarkup()
        subs = api.get_employe_subs(message.from_user.id)
        for sub in subs:
            unsubscribe_inline_keyboard.add(
                types.InlineKeyboardButton(text=sub[0], callback_data="unsub-" + str(sub[1])))
        if subs == []:
            await bot.send_message(message.from_user.id, "Вы пока ни на кого не подписаны!")
        else:
            await message.reply("Выберете пользователя от которого хотите отписаться:",
                                reply_markup=unsubscribe_inline_keyboard)

    if message.text == "Подписаться на всех":
        api.subscribe_all(message.from_user.id)
        await message.reply("Вы успешно подписались на всех пользователей!")
    if message.text == "Отписаться от всех":
        api.unsubscribe_all(message.from_user.id)
        await message.reply("Вы успешно отписались от всех пользователей!")


@dp.callback_query_handler(lambda c: c.data)
async def handle_inline_buttons(callback_query: types.CallbackQuery):
    if callback_query.data.startswith("sub-"):
        api.subscribe_on_user(callback_query.from_user.id, str(callback_query.data).split("-")[1])
        await callback_query.answer("Подписка успешно оформлена!")

    if callback_query.data.startswith("unsub-"):
        api.unsubscribe_on_user(callback_query.from_user.id, str(callback_query.data).split("-")[1])
        await callback_query.answer("Подписка успешно отключена!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
