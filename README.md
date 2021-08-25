<br/>
<br/>
<p align="center">
  <img src="static/img/activity_primary_color.png" height="45" />
</p>

<br/>
<p align="center">
  <a href='https://travis-ci.org/hikaya-io/activity.svg?branch=dev'><img src='https://travis-ci.org/hikaya-io/activity.svg?branch=dev' alt='Travis Status' /></a>
  <a href="https://codecov.io/gh/hikaya-io/activity"><img src="https://codecov.io/gh/hikaya-io/activity/branch/dev/graph/badge.svg" alt="Codecov badge" /></a>
  <a href='https://github.com/hikaya-io/activity/workflows/Activity/badge.svg'><img src='https://github.com/hikaya-io/activity/workflows/Activity/badge.svg' alt='GH Actions Status' /></a>
</p>

<br/>
<p align="center">
  <i>A modern way for nonprofits to manage project activities and indicator results.<br/>Try out Activity using our hosted version at <a href="https://hikaya.io">hikaya.io</a>.</i>
  <br/>
  <br/>
  <img src="static/img/activity_home.png" alt="Activity" width="800" />
</p>
<p align="center">
  <a href="https://spectrum.chat/hikaya" rel="nofollow"><img src="https://withspectrum.github.io/badge/badge.svg" alt="Join the community on Spectrum"/></a>
</p>

This is the source code that runs the [**Activity**](https://hikaya.io/index#content4-8) application. If you want to use Activity then you don't need to run this code, we offer a hosted version of the app at [activity.hikaya.app](https://activity.hikaya.app).

If you'd like to run your own copy of Activity or contribute to its development then this is the place for you.

<!-- ## Configuration
## To deploy changes in activity servers
Once all your changes have been committed to the repo, and before pushing them, run:
`. travis.sh` -->

<br/>
<br/>

# Local Setup

**Note**: You should use `Python 3.7.5` for this project, meaning you may need to use `python3` or `pip3` in the following instructions (you can use the package manager on your OS, brew for mac, to install python 3).

Open up your terminal and follow the instructions listed below.

See [these instructions for additional information](#extra-information).

## Clone the github repository

Navigate to the folder you want the repository to be stored in.

Run the following command:

```bash
$ git clone --branch develop https://github.com/hikaya-io/activity.git
```

Once cloned, navigate to the cloned repository with:

```bash
$ cd activity
```

or similar for your OS.

## Setup the Virtual Environment
You can setup virtual environment either using `virtualenv` or `pipenv`.

### Using virtualenv
```bash
$ pip install virtualenv  # Install virtualenv
$ virtualenv -p python3.7 <myvirtualenvironmentname>  # Create your virtual environment
$ source <myvirtualenvironmentname>/bin/activate  # Activate your virtual environment on Linux...
$ source <myvirtualenvironmentname>/script/activate # ... or on Windows
$ pip install -r requirements.txt  # Install the dependencies
```
### Using pipenv
```bash
$ pip install pipenv  # Install pipenv
$ pipenv shell  # Create and activate the pipenv environment
$ pip install -r requirements.txt  # Install the dependencies
```

### Django local config file

Copy the example config:

```bash
$ cp activity/settings/local-sample.py activity/settings/local.py
```

### Modify the config file

Edit database settings activity/settings/local.py as shown below.

We will change the `ENGINE` parameter to the default value for postgres (although you can also use MySQL or SqlLite3 which is out-of-the-box supported by Django). We also need to add a default database name in the `NAME` option.

Since postgres is the preferred database for this project, we have provided extra instructions to help you set it up. These can be viewed [here](#postgresql-help).

```yaml
47 DATABASES:
48  'default': {
49    #'ENGINE': 'django.db.backends.postgresql', # Alternatives: 'postgresql', 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
50    'ENGINE': "django.db.backends.postgresql"
51    'NAME': os.environ.get('ACTIVITY_CE_DB_NAME', 'mydatabasename'), # replace mydatabasename here with the name of your database
52    # The following can be left unchanged for local use:
53    'USER': os.environ.get('ACTIVITY_CE_DB_USER', ''),
54    'PASSWORD': os.environ.get('ACTIVITY_CE_DB_PASSWORD', ''),
55    'HOST': os.environ.get('ACTIVITY_CE_DB_HOST', ''),
56    'PORT': os.environ.get('ACTIVITY_CE_DB_PORT', ''),
```

### Set up DB

To set up the database, we can use Django's migrations, which take care of propagating the defined models into our database schema:

```bash
$ python manage.py migrate
```

### Create superuser (first time only)

A superuser is necessary to access Django's administration panel.
To create one, use the following:
```bash
$ python manage.py createsuperuser
```

You can use the superuser you created to authenticate into the Django panel in http://localhost:8000/admin once you launch the API.

## Run fixtures

In the `fixtures` folder, you can find JSON files that define sample data to populate the database, after setting its schema.

Here are a few essential fixtures to load:
```bash
$ python manage.py loaddata fixtures/auth_groups.json  # Add authorization groups
$ python manage.py loaddata fixtures/countries.json  # Add countries
$ python manage.py loaddata fixtures/sectors.json  # Add sectors
```

### Run the app locally

If you're using more then one settings file change the `manage.py` file to point to local or dev file first.

```bash
$ python manage.py runserver
```

This will run the server on http://127.0.0.1:8000

### Create an Activity User

Once you have created your user account, you need to create an `Activity User` that is linked to this user account.

Go to http://127.0.0.1:8000/admin and sign in using your superuser account. Under the `Workflow` app, you'll find `Activity users`. Create a new `ActivityUser` instance and make sure you associate your user under the `User` attribute.

### Open the dashboard

Before launching the dashboard on http://127.0.0.1:8000, you need to log out of the admin account first.
This is to avoid an `AttributeError`.

Log in using the same Admin credentials you used on the dashboard login page.

## Set up locally using Docker

### Build the docker images

```bash
$ docker-compose build
```

### Run the container

```bash
$ docker-compose up 
```
You can add the `-d` flag to run the container in detached mode

### Run and Build at the same time
```bash
$ docker-compose up -d --build

If docker is exiting due to postgres connection issues. Stop your local postgres instance, then rerun the above command

```

### Create Superuser
```bash
$ docker-compose exec web python manage.py createsuperuser
```

### Create 'Activity users'
Before logging in to the application, you will need to create an Activity User through Django's Admin Dashboard.
- Go to the Admin dashboard: http://localhost:8000/admin/.
- Navigate to `Workflow > Activity users` and add an Activity user.
- Make to sure to select the superuser name you created earlier.

### Open the dashboard
- Please make sure to log out of the admin console to avoid `AttributeError`.
- Go back to the main page to log in and create an organization to access the main dashboard (http://localhost:8000/)

### To run any other django commands
```bash
$ docker-compose exec web python manage.py [operation]
```
The `operation` in this case can be: `makemigrations`, `migrate`, `collectstatic` etc

<br/>
<br/>

# Contributing

Activity is built and maintained by the team at [Hikaya](https://hikaya.io/team).

Feel free to checkout and learn more about:

- Our [contribution guide](./CONTRIBUTING.md)
- Our [development process](https://team.hikaya.io/start/development-process.html)

We are always looking for a fresh set of :eyes: who want to contribute to **Activity**, so if you are interested, you can reach out and create an issue and we'll help you get started!

<!-- TODO point to Github discussions -->