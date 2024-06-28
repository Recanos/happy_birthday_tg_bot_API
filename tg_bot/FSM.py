from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    waiting_for_date_of_birth = State()  # Определение состояния для ожидания даты рождения
    registration_user = State()
    subscibe = State()
