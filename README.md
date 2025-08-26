# to-do-list-API

RESTful API for managing a to-do list made with Django Rest Framework.\
Implements user authentication based on JSON tokens.

API only supports basic CRUD operations, because it is strongly focused on user authentication practise.

## Table of Contents

- [Local Setup](#local-setup)
- [How to Use](#how-to-use)
- [Endpoints](#endpoints)
- [Key Features](#key-features)
- [How Token Works](#how-tokens-work)
- [Needed Files](#needed-files)
- [Limitations](#limitations)
- [License](#license)
- [Credits](#credits)

## Local Setup

1. Have Python 3.13+ installed
2. Create local enviroment, for example by running `py -m venv venv` in command prompt
3. Activate the enviroment
4. Install dependencies from [requirements.txt](requirements.txt)
5. Run `manage.py makemigrations`
6. Run `manage.py migrate`
7. Run `manage.py runserver`

## How to Use

API only accepts HTTP POST requests.\
A proper JSON (meeting the endpoint criteria) shall be sent to one of the following endpoints.

## Endpoints

See [endpoints.md](docs/endpoints.md)

## Key Features

- Token-based authentication
- Hashing passwords and tokens before saving them to database

## How Tokens Work

When user signs up, a new token is generated for them. It is sent as a response from `/user/signup/` endpoint, hashed and stored in database.

When user is finished using the API, they can log out by sending request to `/user/logout/` view, that will set their `token` filed in database to `logged_out`.

In this state, no operation can be made from this account, until the user log in.

By sending request to `/user/login/` endpoint, new token is generated and assigned to the account, it is again hashed and stored in database. This token can be used to access endpoints responsible for operations on the list.

When logged in, user can get the token by sending email and password to `/user/remindToken/` view.

## Needed Files

Beside `.env` file, `hashes.py` is also needed to set up the program in local enviroment.

This file contains tables for hashing and dehashing strings.

## Limitations

This API uses a .sqlite3 database, which is the default Django database.

It can be easly replaced with any other remote db.

## License

See [LICENSE](LICENSE)

## Credits

Idea from [roadmap.sh](https://roadmap.sh/projects/todo-list-api)
