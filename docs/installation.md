# Installation

> TODO detailed installation guide

1. Development setup with hot reload
2. Python virtual environment and dependencies installation
3. Django config file & Django "superuser" creation

## Recommended setup

```bash
cp activity/settings/local-sample.py activity/settings/local.py
docker-compose up
```

This will launch the Activity app and a PostgreSQL database.

To see how the Activity Docker container is built, please check the [Dockerfile](../Dockerfile).
From inside the Activity Docker container, the script `start.sh` will be executed.
The Activity code is mounted using a [Docker Volume](), which allows your changes to the code to be reflected in the Activity Docker container.

To check the running Docker containers: `docker ps -a`
To inspect and follow the logs: `docker-compose logs -f`
To get a BASH terminal into the Activity container: `docker-compose exec -ti api bash`

## Alternative setup

1. Create a [Python virual environment](https://docs.python.org/3/tutorial/venv.html) and activate it. Make sure you have at least Python 3.7

2. Install dependencies using `pip-tools`. Check our [dependencies documentation](./dependencies.md) on why and how we use `pip-tools` to manage our dependencies.

```bash
pip install pip-tools
pip-tools sync
```

3. Launch a PostgreSQL instance and create a database in it (alternatively `docker-compose up -d db`) 

4. Configure environment variables.
<!-- TODO Which file exactly -->

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
