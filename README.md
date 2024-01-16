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
- [Docker](https://docs.docker.com/get-docker/)
- Python 3.7+, preferably inside a Python virtual environment ([virtualenv](https://virtualenv.pypa.io/en/latest/), [pipenv](https://pipenv.pypa.io/en/latest/) or others)
- Make sure your dependencies are up-to-date. Update depdendencies with

```bash
sudo apt-get update && sudo apt-get -y upgrade # Linux

brew update && brew upgrade # Mac
```

## Recommended setup

> For the sake of similarity between developers environments and the deployment environments, we **strongly** recommend using Docker. For more details, see the Docker [installation guide](https://docs.docker.com/engine/install/).

### Clone the repository and go to Activity directory

```bash
git clone --branch develop https://github.com/hikaya-io/activity.git && cd activity
```

### Copy the settings file

```bash
cp settings/local-sample.py settings/local.py
```

### Launch Activity and its PostgreSQL database

```bash
docker compose up -d
```

This will:

1. Pull needed Docker images
2. Launch PostgreSQL
3. Build and launch Activity
4. Run database migrations on the PostgreSQL instance

It may take a while, but Activity should be accessible at `http://localhost:8080`

This setup is using the environment variables defined in the file `.env.docker-compose`.
You can read more about Activity's expected environments variables in our [installation guide](./docs/installation.md#envvars).

## Post-installation

1. Apply the [Django fixtures](https://docs.djangoproject.com/en/3.2/howto/initial-data/#providing-data-with-fixtures) defined in the `fixtures` folder:

    ```bash
    docker compose exec app python manage.py loaddata fixtures/auth_groups.json  # Add authorization groups
    docker compose exec app python manage.py loaddata fixtures/countries.json  # Add countries
    docker compose exec app python manage.py loaddata fixtures/sectors.json  # Add sectors
    ```

2. Create a Django superuser/admin

   ```bash
   docker compose exec app python manage.py createsuperuser
   ```

   You can now use it to login at http://localhost:8000/admin

3. Signup with a new user on Activity. Activate it through Django Admin Dashboard on `http://localhost:8000/admin/workflow/activityuser/`

You can now set up your favourite reverse proxy and link a domain to expose the app to the public.

# Hosting

You can use any cloud hosting provider of your choice. 
We have used Digital Ocean and used App services to easily deploy the app. Here is the setup documentmention on Digital Ocean for [Django app](https://docs.digitalocean.com/products/app-platform/getting-started/sample-apps/django/). The Digital Ocean Basic plan of 512 MB RAM | 1 vCPU will suffice. Possible option for database config for the app: 1 GB RAM / 1vCPU / 10 GB Disk / Primary only / PostgreSQL 15.

If you want setup from a droplet here are the steps you can follow to set up deployment and hosting:

1. Create an [account](https://cloud.digitalocean.com/registrations/new) on Digital Ocean.
2. Create a [droplet](https://docs.digitalocean.com/products/droplets/how-to/create/). You can select a the Basic Ubuntu plan with at least 4GB RAM as Docker requires at least 4GB RAM droplet. RAM requirement can potentially be reduced by using Dockerhub.
3. Add your SSH key as you create your droplet. This is required to access the server later.
4. Once the droplet is created add your [domain and DNS information](https://docs.digitalocean.com/products/networking/dns/getting-started/quickstart/).
5. Now your droplet is ready for adding your project data. On your local machine `cd` into the root project folder and [copy files](https://www.digitalocean.com/community/tutorials/how-to-use-rsync-to-sync-local-and-remote-directories) over to the server

   ```bash
   rsync -av -e "ssh -i $LINK/TO/SSH_KEY/FILE/DIRECTORY" PROJECT_FOLDER_NAME root@IP.ADDRESS:/root
   ```

6. SSH into your server to check if the files are copied correctly

   ```bash
   ssh -i $LINK/TO/SSH_KEY/FILE/DIRECTORY root@IP.ADDRESS
   ```

7. In your server, install docker. Here are the setup instructions for [Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
8. Copy the settings files

   ```bash
   cp settings/local-sample.py settings/local.py
   ```

9. Then build and run the project on docker

    ```bash
    docker compose up -d
    ```

10. You can check if containers are built correctly and running by running

    ```bash
    docker contain ls -a
    ```

11. Run through the 'post-installation' steps from the above section to make sure all the fixtures are in place.
12. Make sure to add the [environment variables](https://docs.digitalocean.com/glossary/environment-variable/) on Digital Ocean.
13. Your application should be ready and accessible on your domain.

# Contributing

Activity is built and maintained by the team at [Hikaya](https://hikaya.io/team).

Feel free to checkout and learn more about:

- Our [contribution guide](./CONTRIBUTING.md)
- Our [development process](https://team.hikaya.io/start/development-process.html)

We are always looking for a fresh set of :eyes: who want to contribute to **Activity**, so if you are interested, you can reach out in our [issues board](https://github.com/hikaya-io/activity/issues) or [open a Github discussion](https://github.com/hikaya-io/activity/discussions) and we'll help you get started!
