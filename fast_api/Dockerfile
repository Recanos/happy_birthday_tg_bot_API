<<<<<<< HEAD
FROM python:3.8

WORKDIR /fast_api

COPY ./requirements.txt /fast_api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fast_api/requirements.txt

COPY . /fast_api

=======
FROM python:3.8

WORKDIR /fast_api

COPY ./requirements.txt /fast_api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fast_api/requirements.txt

COPY . /fast_api

>>>>>>> 523e111b3b7e89f078dd8941e429c20216035a24
CMD ["uvicorn", "main:app", "--host", "45.141.103.108", "--reload"]