# Используем базовый образ Python
FROM python:3.10

# Установка зависимостей для OS и Python
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# Установка рабочей директории
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем Python зависимости
COPY fast_api/requirements.txt /app/fast_api/requirements.txt
COPY tg_bot/requirements.txt /app/tg_bot/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /app/fast_api/requirements.txt
RUN pip install -r /app/tg_bot/requirements.txt

# Копируем исходный код приложений
COPY . /app

# Устанавливаем переменную окружения для FastAPI
ENV PYTHONPATH=/app

# Команда для запуска FastAPI и бота
CMD ["sh", "-c", "uvicorn fast_api.main:app --host 0.0.0.0 --port 8000 & python3 tg_bot/bot.py"]
