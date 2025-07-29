<h1 align="center">🎵 Music Streamer 🎵</h1>

<p align="center">
  <b>Version 1.0 • A backend-heavy, full-stack music streaming application</b><br>
  <i>Built with FastAPI, Flutter, PostgreSQL etc. </i>
</p>

<p align="center">
  <a href="https://github.com/myndaaa/MusicPlayer-FastAPI"><img src="https://img.shields.io/badge/version-1.0-blue.svg" alt="Version"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.104.1-green.svg?logo=fastapi" alt="FastAPI"></a>
  <a href="https://flutter.dev/"><img src="https://img.shields.io/badge/Flutter-3.22-blue.svg?logo=flutter" alt="Flutter"></a>
  <a href="https://pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2.6.4-yellow.svg?logo=pydantic" alt="Pydantic"></a>
  <a href="https://docs.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-red.svg?logo=sqlalchemy" alt="SQLAlchemy"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg?logo=postgresql" alt="PostgreSQL"></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/pytest-tested-brightgreen.svg?logo=pytest" alt="pytest"></a>
</p>

<p align="center">
  <a href="https://github.com/myndaaa/MusicPlayer-FastAPI"><img alt="GitHub Repo Stars" src="https://img.shields.io/github/stars/myndaaa/MusicPlayer-FastAPI?style=social"></a>
</p>

<p align="center">
  <a href="mailto:mysha.shemontee@monstar-lab.com">
    <img alt="Developer" src="https://img.shields.io/badge/email-mysha.shemontee%40monstar--lab.com-red?logo=gmail&logoColor=white&label=Contact&color=red">
  </a>
</p>

This is a backend heavy Music Streamer made with **FastAPI + PostgreSQL + SQLAlchemy** that allows three user groups (Superusers aka admin, Singers and Listeners) <br> <br>
This small-scale music streaming platform is for artists and listeners. It’s designed to run entirely on free cost cloud services but scalable so that it can still grow if needed. The stack is selected to balance simplicity, cost efficiency, maintainability, and ease of scaling later. <br> <br>
The project although would have a frontend, would be backend heavy, especially relying on FastAPI and its features, hopefully exploring most if not all of its beginner to intermediate features. <br> <br>


## Contents
- [Tech Stacks used in this project](#tech-stacks-used-in-this-project)
-  [Run Manually (Local Dev)](#run-manually-local-dev)
	- [Getting Started - Backend](#getting-started---backend)
	  - [Installing Poetry](#installing-poetry)
	  - [Installing PostgreSQL](#installing-postgresql)
	    - [macOS](#macos)
	    - [Windows](#windows)
	- [Environment Setup](#environment-setup)
	- [Database Migrations](#database-migrations)
	- [Running the Application](#running-the-application)
- [Run with Docker](#run-with-docker)
- [Get to know the system](#get-to-know-the-system)

# Tech Stacks used in this project

| 🏗️ **[FastAPI](https://fastapi.tiangolo.com/)**  | Async Python web framework. High-performance & ASGI-based.                  |
| ------------------------------------------------- | --------------------------------------------------------------------------- |
| 🛡️ **[Pydantic](https://docs.pydantic.dev/)**    | Data validation using Python type hints. Validates request/response models. |
| 🧱 **[SQLAlchemy](https://docs.sqlalchemy.org/)** | ORM and SQL toolkit for handling database models and queries.               |
| 🐘 **[PostgreSQL](https://www.postgresql.org/)**  | Relational database for storing application data.                           |
| 🧬 **[Alembic](https://alembic.sqlalchemy.org/)** | Database migration tool used alongside SQLAlchemy.                          |
| 🧪 **[Pytest](https://docs.pytest.org/)**         | Testing framework for writing backend tests.                                |
| 📦 **[Poetry](https://python-poetry.org/)**       | Dependency & virtualenv manager for Python.                                 |
| 📱 **[Flutter](https://flutter.dev/)**            | Natively compiled mobile/web UI from a single codebase                      |

# 🧪✨ Run Manually (Local Dev)
## Getting Started - backend
This project is using **poetry** as package manager and SqlAlchemy for version control of its database, which is using PSQL. 
</br>
First, we need to clone the repo, open a terminal and go to your desired directory and run the following command to clone the source code from the repository.

```
git clone https://github.com/myndaaa/MusicPlayer-FastAPI.git
```

Note: a prerequisite for the above is to have git added to your system path, if you dont have it follow instructions in accordance to your development machines OS.

</br>

Next up, ensure you have the correct dependencies installed. 
1. Poetry
2. Postgresql

### Installing Poetry
*before installing please [read](#alternatively-you-can-follow-this) and go through the process once having a clear picture of how poetry functions.* </br>
Depending on whether you are in a Mac device or Windows, run the following commands: </br>

**Mac**

```bash
brew install poetry
```

</br>
Windows via curl (can also use pip)

```bash
curl -sSL https://install.python-poetry.org | python -
```
Once done. Add it to the path and then verify your installation with `poetry --version` for both mac and windows. </br>

**Changing to the correct interpreter**

If we have opened the folder where poetry was initiated then visual studio on its own would detect the environment created by poetry and change the interpreters. But if we are not in the folder where poetry was initiated, for example this project. where the folder directory looks like - root folder : `music_streamer` and we have `music_streamer/backend/poetry.toml`

In such case we have to manually change the interpreter so the frameworks that are installed via `Poetry` would be detected.

- Get all poetry env list
   ```bash
   poetry env info --path

   sample output: /Users/mlbd-XX/Library/Caches/pypoetry/virtualenvs/music_streamer-fastapi-abc123-py3.11

   ```
- Press `Cmd + Shift + P` (or `Ctrl + Shift + P` on Windows)
- Search: `Python: Select Interpreter` click it and then click `Enter interpreter path`
- now type the env path found earliar and add `/bin/python` to 

#### Alternatively, you can follow this:


Make Poetry always create virtual envs inside project. This makes it easier to find the venv:
This must be run before doing `poetry init`

```bash
poetry config virtualenvs.in-project true
```

Then future virtual environments will be created inside .venv in the subfolder, like `backend/.venv/bin/python` 
Then we can set interpreter to:

```bash
backend/.venv/bin/python
```

If running this mid project then:

```bash
# enable project venv
poetry config virtualenvs.in-project true

# remove current global venv no data loss
poetry env remove python

# make a fresh `.venv/` 
poetry install
```



### Installing Postgresql

This project uses **PostgreSQL** as the database. Follow these steps to install it on your machine. </br>
For Mac, install using [Homebrew](https://brew.sh/):

```bash
brew install postgresql
```
Start the PostgreSQL service:

```bash
brew services start postgresql

```
Connect to the default postgres database:

```bash
psql postgres
```

Verify installation with 
```bash
psql --version
```

For installing PSQL on Windows, follow these steps

1. Download the installer from [official PostgreSQL site](https://www.postgresql.org/download/windows/).

2. Run the installer:
   - Choose your version.
   - Set a superuser password (**remember this for your `.env` file**).

3. After installation, you can:
   - Use **pgAdmin** (the included graphical tool) to manage your database.
   - Or open the **psql** shell to run commands.

Verify installation with 

```bash
psql --version
```

## Environment Setup

Copy `.env.example` to `.env` and update values as needed:

```bash
cp .env.example .env
```
Then update the variables as needed so the application (alembic and fastapi) understands it

### Installing the environment packages

Install dependencies and activate Poetry shell

```bash
poetry install       # Installs project dependencies added via poetry add <dependency_name>
```
```bash
poetry shell         # Activates the virtual environment
```

Inside the psql shell, we can run all commands directly, this shell is the virtual env shell for poetry, else, we can run poetry commands by setting it as the interpretor on vsCode and using commands as follows:

```bash
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
poetry run pytest
```

## Database Migrations

Login to PostgreSQL 
    
```bash
psql -U postgres
```

- Create the database and user if you haven’t already:
    

```sql
CREATE USER mynda WITH PASSWORD 'dev';
CREATE DATABASE music_stream OWNER mynda;
GRANT ALL PRIVILEGES ON DATABASE music_stream TO mynda;
```


## Running the Application

**Initialize Alembic (already done if cloning repo)**
**Run migrations to create tables**
    
From the project root (where `alembic.ini` is located):

```bash
alembic upgrade head
```

This will apply all migration scripts and create all necessary tables.
**Verify tables are created**
    

Use psql or any PostgreSQL client to check:

```bash
psql -U mynda -d music_stream
\dt
```

# 🐳⚡ Run with Docker

## **Make sure you have Docker installed**

Install [Docker](https://docs.docker.com/get-docker/) for your OS. Verify with the following commands
```bash
docker --version 
docker-compose --version
```
## **Start the docker daemon**
Simply launching the Docker Desktop application will automatically start the Docker daemon.

## Build and run the container
Look at the root folder and make sure it contains the following file `docker-compose.yml`
Then change directory to said root folder and run the following command:
```bash
docker-compose up --build
```
Alternatively check the health of the containers via
```bash
docker compose ps
```
Sample output:
```bash
NAME                COMMAND                  STATE                HEALTH             PORTS
music-db-1          "docker-entrypoint.s…"   Up 30 seconds        healthy            5432/tcp
music-web-1         "uvicorn app.main:ap…"   Up 10 seconds        starting           0.0.0.0:8000->800

```
# Get to know the system

Further details about the system can be found on topic specific markdown files. Based on the requirement kindly click the links below to redirect to the correct document to get explanation of the system in detail.

- [System Documentation](https://docs.google.com/document/d/1OgOAGaGIimPLEj1oWWk97l_t-elVHXK3ed1jDhDiPLA/edit?usp=sharing)
- [About the Project](Documents/about_the_project.md)
- [Application Features](Documents/features.md)
- [System Architecture](Documents/FolderStructure.md)
- [Folder Structure](Documents/FolderStructure.md)
- [Model Development](backend/app/db/README.md)
