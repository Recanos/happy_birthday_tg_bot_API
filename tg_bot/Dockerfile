FROM python:3.8

WORKDIR /tg_bot

COPY ./requirements.txt /tg_bot/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tg_bot/requirements.txt

COPY . /tg_bot

CMD ["python", "./bot.py"]