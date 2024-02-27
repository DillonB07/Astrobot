# Astrobot [![Build status](https://github.com/DillonB07/Astrobot/actions/workflows/ci.yaml/badge.svg?branch=master)](https://github.com/DillonB07/Astrobot/actions/workflows/ci.yaml)

Astrobot is a Discord bot for my college Discord server. It has some fun features and some utilities for us.

### Installation

#### Dependencies

Astrobot uses `pipenv` for dependency and venv management. Install it with `pip install pipenv`, and then run `pipenv install` to install all the required dependencies into a new virtual environment.

#### Development Setup

1. `pipenv install`, as above
2. Copy `config.example.yaml` to `config.yaml` and configure the fields.
3. Copy `alembic.example.ini` to `alembic.ini` and configure any fields you wish to change.
4. Set up the database by running migrations with `alembic upgrade head`.
   - The default database location is `postgresql+psycopg://astro:astro@localhost/astro` (in `config.example.yaml`)
     This requires PostgreSQL to be installed, with a database called `astro` and a user with name and password `astro` with access to it.
   - For testing purposes, you may wish to change it to a locally stored file such as `sqlite:///astro.sqlite3`.
   - Alternatively, see the instructions below for using Docker.
5. On the [Discord Developer Portal](https://discord.com/developers/applications), make sure that your bot has all of the intents enabled.

Run Astrobot using `pipenv run python main.py`

#### Using Docker

A Dockerfile and docker-compose are provided for easily running Astrobot. Assuming you already have docker installed, run `docker compose up` to start both Astrobot and a postgres database.

The compose file uses a read-only bind mount to mount `config.yaml` into the container at runtime, not at build time. Copy `config.example.yaml` to `config.yaml` and configure the fields so that compose can do this. You will need to change the database url to `postgresql+psycopg://astro:astro@db/astro` if you wish to connect to the containerised database. Be sure to configure the rest of the fields too: you need a discord bot token.

The docker image builds `alembic.ini` into it by copying the example, as it is rare any values in this wish to be changed on a per-deployment basis.

When you first create the database container, you'll need to apply migrations:

1. Run `docker compose up -d` to start both services in the background. The python one won't work, but leave it running.
   - When changing any source files, the container will have to be rebuilt: `docker compose up --build`
   - For containers running in the background, you can get the outputs using `docker compose logs`
2. Run `docker compose exec astro alembic upgrade head` to apply the database migrations.
3. Run `docker compose down && docker compose up` to restart both services with the migrations applied.
   - Astrobot will now be running in the foreground

Migrations will need to be re-applied every time the database schema changes.

### Contributing
Feel free to create an issue if you have a suggestion or found a bug.
If you want to implement or fix something yourself, feel free to create a pull request!

### Credits

The new Astrobot rewrite is using code from Apollo which is a Discord bot created for the University of Warwick Computing Society Discord server. You can find the original code [here](https://github.com/uwcs/apollo).
