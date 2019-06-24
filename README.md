Activity [![Build Status](https://travis-ci.org/hikaya/Activity-CE.svg?branch=master)](https://travis-ci.org/hikaya/Activity-CE)
====

We are developing a tool for humanitarians to manage project activities and indicator results across their programs, including approval workflows and reporting and visualizations. Our goal is to help organizations answer common questions such as:
* who are funding your projects?
* who you work with?
* where you work?
* how do my outputs align with my overall project goal?

## Configuration
Copy the activity/settings/local-sample.py to local.py and modify for your environment.

## To deploy changes in activity servers
Once all your changes have been commited to the repo, and before pushing them, run:
`. travis.sh`

## To deploy localy via Docker
Run the following commands from the root of this repository:

NB: Ensure you have docker installed on your machine
  - `docker-compose build .`
  # run  migrations
  - `docker-compose run web python /code/manage.py migrate --noinput`
  # create superuser
  - `docker-compose run web python /code/manage.py createsuperuser`
  # start the app
  - `docker-compose up -d --build`
  # open on browser
  - `http://127.0.0.1:8000/`

## USING virtualenv
(Install virtualenv)
```bash
$ pip install virtualenv
```


# Create Virtualenv
```bash
$ virtualenv --no-site-packages venv
```
* use no site packages to prevent virtualenv from seeing your global packages
* . venv/bin/activate allows us to just use pip from command line by adding to the path rather then full path

## Activate Virtualenv
```bash
$ source venv/bin/activate
```


## Fix probable mysql path issue (for mac)
export PATH=$PATH:/usr/local/mysql/bin
* or whatever path you have to your installed mysql_config file in the bin folder of mysql

## Install Requirements
```bash
$ pip install -r requirements.txt
```


## Modify the config file
Edit database settings settings/local.py

```yaml
47 DATABASES:
48  'default': {
49    #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
50    'ENGINE': "django.db.backends.mysql"
51    'NAME': "activity"
52    'USER': "root"
53    'PASSWORD': 'password',
54    'HOST': "localhost"
55    'PORT': '',
```
* Replace user and password by your Mysql username and password 

## Set up Django's MySQL backing store

```sql
CREATE DATABASE 'activity';
CREATE USER 'root';
GRANT ALL ON ctivity.* TO 'root'@'localhost' IDENTIFIED BY 'root';
```
* When you use these SQL queries, beware of not writting the quotes.

## Set up DB
```bash
$ python manage.py migrate
```
* If you get access denied, it means you need to modify the config file and write your Mysql username and password in the file

# Run App
If your using more then one settings file change manage.py to point to local or dev file first
```bash
$ python manage.py runserver
```


GOOGLE API
```bash
$ sudo pip install --upgrade google-api-python-client
```

* 0’s let it run on any local address i.e. localhost,127.0.0.1 etc.
