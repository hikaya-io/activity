#!/bin/sh

echo "+++++++++++++++++ Copy Settings File ++++++++++++++++++++++++"
ls activity/settings/
cp activity/settings/local-sample.py activity/settings/local.py
ls activity/settings/
echo "------------------- Copying Settings file Done!!! ------------------------"

echo "+++++++++++++++++ Initialize database migrations ++++++++++++++++++++++++"
python manage.py makemigrations
echo "------------------- Initialize database migrations Done!!! ------------------------"

echo "+++++++++++++++++ Make migrations ++++++++++++++++++++++++"
python manage.py migrate
echo "------------------- Make migrations Done !!! ------------------------"

echo "+++++++++++++++++ Start up the server ++++++++++++++++++++++++"
python manage.py runserver 0.0.0.0:8000
echo "------------------- Development server up and running ------------------------"
