<br/>
<br/>
<p align="center">
  <img src="https://s3.hikaya.io/activity/activity-wordmark.png" height="45" />
</p>

<br/>
<p align="center">
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
  <a href="https://github.com/hikaya-io/activity/discussions" rel="nofollow"><img src="https://img.shields.io/badge/join%20the%20community-in%20Discussions&?style=for-the-badge&logo=github&color=4B3EF9" alt="Join the community on Github Discussions"/></a>
</p>

This is the source code that runs the [**Activity**](https://hikaya.io/index#content4-8) application. If you want to use Activity then you don't need to run this code, we offer a hosted version of the app at [activity.hikaya.app](https://activity.hikaya.app).

If you'd like to run your own copy of Activity or contribute to its development, then this is the place for you.

<br/>

# Getting started

## Requirements and recommendations

- Git
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.7+, preferably inside a Python virtual environment ([virtualenv](https://virtualenv.pypa.io/en/latest/), [pipenv](https://pipenv.pypa.io/en/latest/) or others)

## Recommended setup

> For the sake of similarity between developers environments and the deployment environments, we **strongly** recommend using [Docker Compose](https://docs.docker.com/compose/). For more details, see our [installation guide](./docs/installation).

Clone the repository and launch Activity and its PostgreSQL database using the following:

```bash
git clone --branch develop https://github.com/hikaya-io/activity.git && cd activity
cp activity/settings/local-sample.py activity/settings/local.py
docker-compose up
```

This will:

1. Pull needed Docker images
2. Launch PostgreSQL
3. Build and launch Activity
4. Run database migrations on the PostgreSQL instance

It may take a while, but Activity should be accessible at http://localhost:8080

This setup is using the environment variables defined in the file `.env.docker-compose`.
You can read more about Activity's expected environments variables in our [installation guide](./docs/installation.md#envvars).

## Post-installation

1. Apply the [Django fixtures](https://docs.djangoproject.com/en/3.2/howto/initial-data/#providing-data-with-fixtures) defined in the `fixtures` folder:

```bash
docker-compose exec app python manage.py loaddata fixtures/auth_groups.json  # Add authorization groups
docker-compose exec app python manage.py loaddata fixtures/countries.json  # Add countries
docker-compose exec app python manage.py loaddata fixtures/sectors.json  # Add sectors
```

2. Create a Django superuser/admin: `docker-compose exec app python manage.py createsuperuser`. You can now use it to login at http://localhost:8000/admin
3. Signup with a new user on Activity. Activate it through Django Admin Dashboard on http://localhost:8000/admin/workflow/activityuser/

# Contributing

Activity is built and maintained by the team at [Hikaya](https://hikaya.io/team).

Feel free to checkout and learn more about:

- Our [contribution guide](./CONTRIBUTING.md)
- Our [development process](https://team.hikaya.io/start/development-process.html)

We are always looking for a fresh set of :eyes: who want to contribute to **Activity**, so if you are interested, you can reach out in our [issues board](https://github.com/hikaya-io/activity/issues) or [open a Github discussion](https://github.com/hikaya-io/activity/discussions) and we'll help you get started!
