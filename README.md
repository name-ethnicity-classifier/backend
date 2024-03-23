# Name-to-Ethnicity Backend
This repository contains the backend code of www.name-to-ethnicity.com.

## ⬇️ Setup:
### 1. Clone repository:
```
git clone git@github.com:name-ethnicity-classifier/backend.git
```
### 2. Create and activate environment:
```
python3 -m venv .venv
source .venv/bin/activate
```
### 3. Install requirements:
```
pip3 install -r requirements.txt
```
### 4. Setup .env variables:
Create a file called ".env" in the root folder.
Add the following variables (these are dummy values which can be used during development but DON'T use them for deployment):

```conf
# Variables for REST API
FLASK_RUN_PORT=8080
FLASK_APP=src/app.py

# Variables for JWT
JWT_SECRET=supersecret
JWT_EXPIRATION_DAYS=30

# Variables for dev. database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pwd123
POSTGRES_DB=n2e-db
POSTGRES_PORT=5432
ADMINER_PORT=6060
```

## 🏃 Run locally:
```
python3 -m flask run
```
The server runs now at "localhost:8080".

## 🐳 Running a development database:
If you need to develop CRUD features, you'll need to run a Postgres database in parallel for testing and development.

### 1. Install Docker:
You can install it from [here](https://docs.docker.com/get-docker/).

### 2. Setup .env variables:
Create a file called ".env" in the "dev-database" folder.
Add the following variables (these are dummy values which can be used during development but DON'T use them for deployment):
Make sure that the ".env" in the root folder has the same values for the DB variables as this ".env"!

```conf
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pwd123
POSTGRES_DB=n2e-db
POSTGRES_PORT=5432
ADMINER_PORT=6060
```

### 3. Start the Postgres DB and Adminer UI:
```
sh ./run_dev_db.sh
```

If you need to reinitialize the database (ie. removing existing containers and volumes), run:
```
sh ./run_dev_db.sh --remove
```

This script will run the docker-compose file inside the ``./dev_database``. If you encount any errors that point to missing Postgres environment variables, you might need to copy the ``.env`` into the ``./dev_database``.


The port of the database and Adminer UI depend on what you specified in the .env file, but by default the database will be accessible on ``localhost:5432`` and the Adminer UI on ``localhost:6061``.

This database is persistent, so when you add data it will stay until you delete it.
