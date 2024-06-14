from aiogram import types

from API import API

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add("авторизироваться!")


enter_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
enter_keyboard.row("Подписаться на пользователя", "Отписаться от пользователя")
enter_keyboard.row("Подписаться на всех", "Отписаться от всех")

main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("Подписаться на всех")




