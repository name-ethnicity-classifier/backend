[![Test and Build](https://github.com/name-ethnicity-classifier/backend/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/name-ethnicity-classifier/backend/actions/workflows/ci.yml)

# Name-to-ethnicity Backend
This repository contains the backend code of www.name-to-ethnicity.com.

## 🏃 Setup and run for development:
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
Copy the ``.example.env`` to a ``.env``.

### 5. Start the server:
```
flask run
```

### 6. Start development database:
If you need to develop CRUD features, you'll need to run a Postgres database in parallel for testing and development.
Make sure you have [docker](https://docs.docker.com/get-docker/) installed.

To start the database and Adminer UI run:
```
sh ./run_dev_db.sh
```

If you want to reinitialize the database and remove the current data, run:
```
sh ./run_dev_db.sh --init
```
This script will run the docker-compose file inside the ``./dev_database``. If you encount any errors that point to missing Postgres environment variables, you might need to copy the ``.env`` into the ``./dev_database``.

## 🧪 Testing:
For unit and integration tests make sure you have an instance of the development database running and run:
```
pytest
```
Optionally, for a nicer view use the ``--it`` flag.
