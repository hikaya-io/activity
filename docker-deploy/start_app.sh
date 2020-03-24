#!/bin/bash

echo "+++++++++++++++++ Export environment variables ++++++++++++++++++++++++"
source .env.deploy
echo "+++++++++++++++++ Export Done ++++++++++++++++++++++++"

echo "+++++++++++++++++ Initialize database migrations ++++++++++++++++++++++++"
python manage.py makemigrations
echo "------------------- Initialize database migrations Done!!! ------------------------"

echo "+++++++++++++++++ Make migrations ++++++++++++++++++++++++"
python manage.py migrate
echo "------------------- Make migrations Done !!! ------------------------"

echo "+++++++++++++++++ Start up the server ++++++++++++++++++++++++"
python manage.py runserver 0.0.0.0:8000
echo "------------------- Development server up and running ------------------------"
