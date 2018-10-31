Tola Activity [![Build Status](https://travis-ci.org/toladata/TolaActivity.svg?branch=master)](https://travis-ci.org/toladata/TolaActivity)
====
http://toladata.com/products/activity/

TolaActivity extends the functionality of TolaData to include a set of forms and
reports for managing project activities for a Program.  It includes workflow for approving
and completing projects as well as sharing the output data.


TolaActivity functionality http://www.github.com/toladata/TolaActivity is intended to allow importing
and exporting of project specific data from 3rd party data sources or excel
files.

## Configuration
Copy the tola/settings/local-sample.py to local.py and modify for your environment.

## To deploy changes in activity servers
Once all your changes have been commited to the repo, and before pushing them, run:
`. travis.sh`

## To deploy locally via Docker
Run the following commands from the root of this repository:
  - `docker-compose build`
  - `docker-compose up`

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

Edit _config/settings.secret.yml_. Find the node named, "DATABASES" and set the 
database `PASSWORD` as appropriate. The result should resemble the following:

```yaml
47 DATABASES:
48  'default': {
49    #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
50    'ENGINE': "django.db.backends.mysql"
51    'NAME': "tola_activity"
52    'USER': "root"
53    'PASSWORD': 'tolageek',
54    'HOST': "localhost"
55    'PORT': '',
```
* Replace user and password by your Mysql username and password 

## Set up Django's MySQL backing store

```sql
CREATE DATABASE 'tola_activity';
CREATE USER 'root';
GRANT ALL ON tola_activity.* TO 'root'@'localhost' IDENTIFIED BY 'tolageek';
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
