FROM python:2.7

WORKDIR /code

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt