# Pull base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/activity

RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf

# make psycopg2-binary install on alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1 #Prevents Python from writing pyc files to disc
ENV PYTHONUNBUFFERED 1 #Prevents Python from buffering stdout and stderr

# Set environment variables
ENV ACTIVITY_CE_DB_ENGINE=django.db.backends.postgresql
ENV ACTIVITY_CE_DB_NAME=activity_dev
ENV ACTIVITY_CE_DB_USER=activity
ENV ACTIVITY_CE_DB_PASSWORD=activity
ENV ACTIVITY_CE_DB_HOST=db
ENV ACTIVITY_CE_DB_PORT=5432

# Fix of https://github.com/pyca/cryptography/issues/5771
# starting cryptography>=3.5, Rust is required to build it (or a later version of PIP for wheel download)
# Updating cryptography requries Rust installation
# In cryptography < 3.5, which we use, it can be disabled using the below env var
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/activity/requirements.txt
RUN pip install -r requirements.txt

# Copy project.
COPY . /usr/src/activity/
