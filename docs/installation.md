# Installation

> TODO detailed installation guide

1. Development setup with hot reload
2. Python virtual environment and dependencies installation
3. Django config file & Django "superuser" creation
4. Running migrations & fixtures
5. Gaining access to local Activity instance


1. Running Activity locally and PostgreSQL using Docker Compose


## Recommended setup


Checks logs and -f
Check containers
Get a bash terminal

## Alternative setup

1. Create a [Python virual environment](https://docs.python.org/3/tutorial/venv.html) and activate it. Make sure you have at least Python 3.7

2. Install dependencies using `pip-tools`. Check our [dependencies documentation](./dependencies.md) on why and how we use `pip-tools` to manage our dependencies.

```bash
pip install pip-tools
pip-tools sync
```

3. Launch a PostgreSQL instance and create a database in it (alternatively `docker-compose up -d db`) 

4. Configure environment variables. See more details
<!-- Which file exactly -->

5. Make and apply migrations

```bash
python manage.py makemigrations && python manage.py migrate
```

6. Apply fixtures:
```
python manage.py loaddata fixtures/auth_groups.json
python manage.py loaddata fixtures/countries.json
python manage.py loaddata fixtures/sectors.json
```

## Install non-python dependencies

1. **GDAL**

On MacOs:

```bash
$ brew install gdal
```

On Windows:
- You will need to download Gdal Core and Gdal installer for your version of Python.
- Please read the following [instructions](https://pypi.org/project/GDAL/#windows) on how to properly install and test gdal.

2. **Pango**

On MacOs:

```bash
$ brew install pango
```

On Windows:
- You will need Pango and Cairo for the application to run.
- The runtime installer can be found [here](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- Download and install GTK+-3. 
