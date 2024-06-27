FROM python:3.8

WORKDIR /fast_api

COPY ./requirements.txt /fast_api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fast_api/requirements.txt

COPY . /fast_api

CMD ["uvicorn", "main:app", "--host", "45.141.103.108", "--reload"]