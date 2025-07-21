# Music Streamer
This is a backend heavy Music Streamer made with **FastAPI + PostgreSQL + SQLAlchemy** that allows three user groups (Superusers aka admin, Singers and Listeners) <br> <br>
This small-scale music streaming platform is for artists and listeners. It’s designed to run entirely on free cost cloud services but scalable so that it can still grow if needed. The stack is selected to balance simplicity, cost efficiency, maintainability, and ease of scaling later. <br> <br>
The project although would have a frontend, would be backend heavy, especially relying on FastAPI and its features, hopefully exploring most if not all of its beginner to intermediate features. <br> <br>


## Contents
- [Tech Stacks used in this project](#tech-stacks-used-in-this-project)
- [Getting Started - Backend](#getting-started---backend)
  - [Installing Poetry](#installing-poetry)
  - [Installing PostgreSQL](#installing-postgresql)
    - [macOS](#macos)
    - [Windows](#windows)
- [Environment Setup](#environment-setup)
- [Database Migrations](#database-migrations)
- [Running the Application](#running-the-application)
- [Development Conventions of the codebase](#development-conventions-of-the-codebase)
- [Get to know the system](#get-to-know-the-system)

## Tech Stacks used in this project

- **FastAPI** : A wrapper around starlette and pydantic hence known to be quite fast than other frameworks which run on WSGI instead of ASGI. As this is a music streamer, it having low response time is a crucial part of end user satifaction, FastAPI has been chosen as the backend framework.
- **PostgreSQL** : Psql

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

**Changing to the correct interpretor**

If we have opened the folder where poetry was initiated then visual studio on its own would detect the environment created by poetry and change the interpretorss. But if we are not in the folder where poetry was initiated, for example this project. where the folder directory looks like - root folder : `music_streamer` and we have `music_streamer/backend/poetry.toml`

In such case we have to manually change the interpretor so the frameworks that are installed via `Poetry` would be detected.

- Get all poetry env list
   ```bash
   poetry env info --path

   sample output: /Users/mlbd-XX/Library/Caches/pypoetry/virtualenvs/music_streamer-fastapi-abc123-py3.11

   ```
- Press `Cmd + Shift + P` (or `Ctrl + Shift + P` on Windows)
- Search: `Python: Select Interpreter` click it and then click `Enter interpreter path`
- now type the env path found earliar and add `/bin/python` to 

#### Alternatively, you can follow this:**


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

## Database Migrations

## Running the Application

## Development Conventions of the codebase
 - System uses python convention and uses snake cases (eg: `user_account_link`)
 - currently system uses space indentation instead of tab indentation

## Get to know the system

Further details about the system can be found on topic specific markdown files. Based on the requirement kindly click the links below to redirect to the correct document to get explanation of the system in detail.

- [System Documentation](https://docs.google.com/document/d/1OgOAGaGIimPLEj1oWWk97l_t-elVHXK3ed1jDhDiPLA/edit?usp=sharing)
- [About the Project](Documents/about_the_project.md)
- [Application Features](Documents/features.md)
- [System Architecture](Documents/FolderStructure.md)
- [Folder Structure](Documents/FolderStructure.md)
- [Model Development:](backend/app/db/README.md)