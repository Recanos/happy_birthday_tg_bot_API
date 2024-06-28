<<<<<<< HEAD
from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    waiting_for_date_of_birth = State()  # Определение состояния для ожидания даты рождения
    registration_user = State()
=======
from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    waiting_for_date_of_birth = State()  # Определение состояния для ожидания даты рождения
    registration_user = State()
>>>>>>> 523e111b3b7e89f078dd8941e429c20216035a24
    subscibe = State()