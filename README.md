# MusicPlayer-FastAPI
<<<<<<< HEAD
A backend heavy Music Player made with FastAPI + PostgreSQL + SQLAlchemy that allows three user groups (Superusers aka admin, Singers and Listeners) )


Full System Documentation can be found [here](https://docs.google.com/document/d/1OgOAGaGIimPLEj1oWWk97l_t-elVHXK3ed1jDhDiPLA/edit?usp=sharing)
=======
This is a backend heavy Music Player made with FastAPI + PostgreSQL + SQLAlchemy that allows three user groups (Superusers aka admin, Singers and Listeners) <br>
This is a small-scale music streaming platform for artists and listeners. It’s designed to run entirely on free cost cloud services but scalable so that it can still grow if needed. The stack is selected to balance simplicity, cost efficiency, maintainability, and ease of scaling later. <br>
The project although would have a frontend would be heavy backend, especially relying on FastAPI and its features, hopefully exploring most if not all of its beginner to intermediate features. <br>


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

## Tech Stacks used in this project


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

Depending on whether you are in a Mac device or Windows, run the following commands: </br>

Mac

```bash
brew install poetry
```

</br>
Windows via curl (can also use pip)

```bash
curl -sSL https://install.python-poetry.org | python -
```
Once done. Add it to the path and then verify your installation with `poetry --version` for both mac and windows. </br>

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

>>>>>>> c7367bd (Updated Readme.md to include)
