# Cocktail app

In this application, users can share their cocktail recipes.

## Core functionality

- User can create an account and log in to the application
- User can add, edit and remove cocktail recipes
  - Each recipe contains
    - a title
    - a list of ingredients
    - ~~a type of glass~~
    - preparation instructions
- User can view a list of all recipes that have been created
- User can add one or more tags to recipes (e.g. sweet, warm, non-alcoholic)
- User can search recipes by a keyword (free-text search)
- There is a user page, which
  - shows how many recipes the user has created
  - contains a list of recipes the user has created
- User can add reviews to recipes from other users
  - The reviews are listed on the cocktail details page
  - A review includes a rating on a scale from 1 to 5
  - An average rating is shown on main list and on the cocktail details page

## Extended functionality ("wishlist")

- User can add a picture to a recipe they have created
- User can filter the list of recipes by
  - ~~a type of glass~~
  - a user added tag
- User can sort the list of recipes by
  - creation date
  - average rating
- Latest / highest rated recipes are highlighted on the main page

## Local development environment setup

### Prerequisites

The application requires a sqlite database. You can create one using the following script:

```
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

The application requires a secret key for session management. You can use the following script to generate a random key:

```
export SECRET_KEY=`python3 -c 'import secrets;print(secrets.token_hex(16))'`
```

### Option 1: With Poetry

The application is developed using [Poetry](https://python-poetry.org/docs/) (version 2.3.2).

Install dependencies

```
poetry install
```

(Optional) Initialize the database with seed data
```
poetry run python seed.py
```

Run the application

```
poetry run flask run
```

### Option 2: Without Poetry

Create and activate a new virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

(Optional) Initialize the database with seed data
```
python3 seed.py
```

Run the application

```
flask run
```
