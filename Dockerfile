FROM python:3.10-slim
LABEL maintainer="UtteRus@mail.ru"
ENV PYTHONUNBUFFERED 1
ENV LANG ru_RU.UTF-8

RUN apt-get update && apt-get install --no-install-recommends -y

WORKDIR /code
COPY . /code

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
