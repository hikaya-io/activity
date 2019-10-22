#official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /root/Downloads/django-on-docker/activity_ce


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk --update --upgrade add gcc musl-dev  jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf 	 

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /root/Downloads/django-on-docker/activity_ce/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /root/Downloads/django-on-docker/activity_ce/entrypoint.sh

# copy project
COPY . /root/Downloads/django-on-docker/activity_ce

ENTRYPOINT ["/root/Downloads/django-on-docker/activity_ce/entrypoint.sh"]
