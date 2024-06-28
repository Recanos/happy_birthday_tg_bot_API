<<<<<<< HEAD
FROM python:3.8

WORKDIR /tg_bot

COPY ./requirements.txt /tg_bot/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tg_bot/requirements.txt

COPY . /tg_bot

=======
FROM python:3.8

WORKDIR /tg_bot

COPY ./requirements.txt /tg_bot/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tg_bot/requirements.txt

COPY . /tg_bot

>>>>>>> 523e111b3b7e89f078dd8941e429c20216035a24
CMD ["python", "./bot.py"]