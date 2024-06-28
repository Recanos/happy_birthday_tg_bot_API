# happy_birthday_tg_bot_API
Сервис, реализующий систему подписки сотрудников друг на друга с целью получения уведомления о событии (день рождения) интересующего вас сотрудника! Так же для удобства пользования и демонстрации работы написан тг бот.
## Проект лежит на сервере и уже запущен!
- обращение к API осуществляется по адресу: http://45.141.103.108:8000  (http://45.141.103.108:8000/docs - красивая документация с описанием методов)
- https://t.me/employee_happy_birthday_bot - ссылка на бота

ссылка на группу может прийти не сразу, а на второй раз после нажатия /start

**Примечание**

Docker в проекте расчитан для развёртывания на сервере по адресу http://45.141.103.108:8000, чтобы запустить на локальном сервере или иначе, нужно изменить параметры в файлах. Так же в боте нужно изменить ссылку для обращения по API.

## Запуск проекта

### С использованием Docker

1. **Сборка Docker-контейнеров:**
```sh
   docker-compose build
```

2. **Запуск Docker-контейнеров:**
```sh
   docker-compose up
```

### Локальный запуск 

### С использованием Docker

1. **Установка зависимостей для FastAPI:**
```sh
      cd happy_birthday_tg_bot_API/fast_api pip install -r requirements.txt
```

2. **Установка зависимостей для телеграм бота:**
```sh
      cd ../tg_bot pip install -r requirements.txt
```

3. **Запуск FastAPI:**
```sh
      cd ..
      uvicorn fast_api.main:app --reload
```

4. **Запуск бота:**
```sh
      python3 tg_bot/bot.py
```
