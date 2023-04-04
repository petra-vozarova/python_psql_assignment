# PSQL DB, Python Data Reader

## Pre-requisites

- Environment with `Python3.6` installed, along with `PostgreSQL 10+`
- Python libraries: `psycopg2` (or `psycopg2-binary`) and `dotenv`
- Data file `configClear_v2.json`

## Running locally

Install the dependencies from `requirements.txt` file
```
python -m pip install -r requirements.txt
```

Due to data confidentionality, data was not pushed into this repository. Import the data file into `/data` folder inside the repository.

Create a PSQL database from Postgres CLI using
```
CREATE DATABASE database_name
```

and store all relevant configuration data in a `.env` file. As an example:

```
PG_HOST=localhost
PG_PORT=5432
PG_USER=your_user
PG_PASSWORD=your_password
PG_DATABASE=your_database
```

Please, make sure that your DB is up and running.

Then run the code using
```
python main.py
```

## Testing

To run tests go to the main directory and run
```
pytest -v
```

The testing checks some basic information, such as wether a correct number of entries have been created, or wether the input file contains expected interfaces.

Each test creates its own instance of a database, so it is run in a complete isolation.
