- [Quick Install](#quick-install)
- [Links](#links)
- [Purpose](#purpose)
  - [Rules](#rules)
  - [Statistics](#statistics)
  - [Language Support](#language-support)
  - [Administration Support](#administration-support)
- [Development](#development)
  - [Virtual environment](#virtual-environment)
  - [Dependencies](#dependencies)
  - [Database](#database)
  - [Translation [optional]](#translation-optional)
- [Website](#website)
- [Testing](#testing)
  - [Install heroku](#install-heroku)
- [Running Locally](#running-locally)
  - [Static website](#static-website)
  - [Heroku Local](#heroku-local)
- [Repository Management](#repository-management)
  - [Workflow](#workflow)
- [Postgresql](#postgresql)
- [References](#references)

# Quick Install

```
git clone https://github.com/ryanwhite04/chengyule.git
cd chengyule
python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
echo TRANSLATION_KEY=$(heroku config:get TRANSLATION_KEY -a chengyule) >> .env # Optional, only if have heroku
flask db upgrade
flask languages upgrade
flask run
```

# Links

- [Heroku](https://chengyule.herokuapp.com/)
- [Github](https://github.com/ryanwhite04/chengyule)

# Purpose

This web application allows users to have a better understanding at traditional chinese 成语.

Each "chengyu" is a 4 character idiom in chinese.

The puzzle itself is written using the custom web components API now available in most browsers.

The nav bar has a "Home" tab which generates a different puzzle, daily, shared amongst all users, while the "Random" tab generates a random puzzle each time it is clicked.

## Rules

The "Rules" tab explains the game rules and includes an example of the game partially played by leveraging the games ability to restart from a previous state stored in local storage

## Statistics

This tab presents user's gaming history -- that is the number of attempts, corrects and fails, aswell as statistics on all users.

It is only shown to logged in users

Statistics are only shown to users who have account, but anonymous users still have their games cached locally incase they reload the page or want to come back to a game later.

It also includes aggragated usage statistics, how many games played by everyone and so on

## Language Support
In order to offer clues to users, tooltips are available for all the chinese character options and a translation of the chengyu itself is provided.

These are available in up to 111 languages which can be added by running

```bash
flask languages add en
```

or replacing en with any of the other language codes showin in languages/index.json

They can also be added manually by editing "languages/allowed", where each line will add a language to the website, and the first line is the default language. This must be folloed by

```
flask languages upgrade
```

in order to take effect

Any translated word is initially fetched from google translation API, but is then cached on the databased for subsequent visits, and any manual translations written into the files in "languages" such as "languages/en.json" are automatically added to the site by

```
flask languages translate en
```

for a single language or

```
flask languages upgrade
```

to update all languages

## Administration Support

In order to become an administrator, create an account and then use the flask admin cli tools

```bash
flask admin update some_cool_username -r 0
```

Will update the "role" to 0 which is maximum (administrator)

Afterwards, reloading the page you will have access to "administation tab in the navbar

This is currently just a list of all tables and rows, but it should be easy to swap rows with forms to allow updating the database from admin panel, ideally into a restful api/ route in it's own blueprint

Currently it's just used for easily monitoring changes and vetting translations

# Development

## Virtual environment

```python3.9 -m venv venv```
```. ./venv/bin/activate```

## Dependencies

*This command should only be run once the environment has been activated*
*You should see (venv) at the start of your command line*

```pip install -r requirements.txt```

## Database

Make sure database is up to date

```flask db upgrade``` to upgrade the database

## Translation [optional]

Add a TRANSLATION_KEY key to your .env if there isn't one there already

If you don't have one, you can get one from [here](https://cloud.google.com/translate/docs/setup) or ask me for one, there will be one in .env when this project is submitted

```flask languages upgrade``` To upgrade language support

# Website

```flask run``` to run the website

# Testing

To run all tests
```bash
python -m unittest discover
```

To run some tests
```
python -m unittest test.test_modules.py
```

To run one test
```
python -m unittest test.test_module.PlayModelCase.test_secondPlay
```

## Install heroku

This is only needed if you want to push the site so that it goes live
You can still work on it locally without this, and this isn't necessary for the assignment it's just for fun

You can try following [Heroku's Guide](https://devcenter.heroku.com/articles/getting-started-with-python#set-up) but that didn't work for me because i'm using WSL2 on windows and it throws an error.

If you get an error too, you can just try
```curl https://cli-assets.heroku.com/install-ubuntu.sh | sh```
but this wont autoupdate or anything
also, here is a [link](https://cli-assets.heroku.com/install.sh) to the script if you want to take a look before installing it

App is currently hosted at [chengyule.herokuapp.com](https://chengyule.herokuapp.com/)

To push to heroku
```bash
git push heroku
```

# Running Locally

## Static website

**Deprecation Notice**
Due to lack of time, support for the static website is dropped, while focussing on the dynamic heroky website

If you just want to mess around with the "selection-puzzle" web component and add some features, you don't need to run flask or anything.
You can just ```cd``` into the ```static``` directory and run ```python -m http.server``` and visit [localhost:8000](http://localhost:8000) in your browser

Right now I'm using google's [Lit](https://lit.dev/) web-component library
It's really nice and makes great reusable web-components at only 5KB.
Since this isn't on the allowed list of technologies for this assignment it will have to be removed before submission though.

I'll probably just swap to using the browsers inbuilt [Custom Elements](https://web.dev/custom-elements-v1/) which is just missing the automatic getter/setter stuff, the tagged template literal html library and some lifecycle methods, but it's still really good.

I've also linked this static website to netlify so once main is pushed to the github repo you can visit it at [chengyu.netlify.app](https://chengyu.netlify.app)

## Heroku Local

If you installed heroku, you can run it through that too using 

```heroku local```

It just looks in the *Procfile* and sees "web: gunicorn app:app" and runs the webapp using gunicorn which is in python dependancies

This is useful for debugging any errors that might be causing the remote heroku dynamos to fail

To see remote logs, ```heroku logs --tail``

# Repository Management

We are using git, and everything is stored on github at [github.com/ryanwhite04/chengyule.git](https://github.com/ryanwhite04/chengyule.git).
It's a private repo since i'm guessing we aren't allowed to share our code with other groups until after assessment has been marked, but if your an assessor reading this, just email me at [ryanwhite04@gmail.com](ryanwhite04@gmail.com) and I can grant you access to the repo

## Workflow

Since there are 3 of us, probably not a good idea to all be pushing to main whenever we want.

Previously I've used the [Gitflow workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) but it's kind of confusing and this is just a small project, so I recommend using instead the [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) which is basically as follows:

- Make a new branch for your feature ```git checkout -b my-fancy-new-feature main```
- Make edits and add save them ```git add <some-file>; git commit;```
- Push your feature branch to the remote repo: ```git push -u origin my-fancy-new-feature```
- When it's all good, push again ```git push```, and get the team to take a look (can use a pull request if you want)
- Merge it into main ```git checkout main; git pull; git pull origin my-fancy-new-feature; git push```

The merging and pull requesting can also be done through Github's website

# Postgresql

To use postgresql you need to install it first, instructions [here](https://devcenter.heroku.com/articles/heroku-postgresql)

Add

```env
DATABASE_URL=postgres:///ryanwhite04
```

replacing "ryanwhite04" with your computers username
If you don't know what your username is, you can run

```shell
echo $(whoami)
```

or just do
```shell
echo DATABASE_URL=postgres:///$(whoami) >> .env
cat .env
```

The app works fine with sqlite, but it's good to test it locally on postgres too since that is what heroku is using

# References

- [alembic](https://alembic.sqlalchemy.org/en/latest/): Database versioning
- [click](https://click.palletsprojects.com/en/8.1.x/): For the CLI for language and admin stuff
- [email-validator](https://pypi.org/project/email-validator/): Registration email validation
- [Flask](https://flask.palletsprojects.com/en/2.1.x/): Main Framework used
- [Flask-Language](https://flask-language.readthedocs.io/en/latest/): Translation
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/): User authentication and management
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/): Database revision history
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) Integration with SQLAlchemy
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/): Integratoin with WTForms
- [gunicorn](https://gunicorn.org/): Server used on heroku, production level
- [Jinja2](https://palletsprojects.com/p/jinja/): For templates
- [Mako](https://www.makotemplates.org/)
- [psycopg2-binary](https://www.psycopg.org/docs/): For the postgres engine for heroku
- [python-dotenv](https://pypi.org/project/python-dotenv/): For Environment Variable configuration
- [requests](https://docs.python-requests.org/en/latest/): TO interact with google translate API aswell as for views/routes
- [SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/tutorial.html): Database ORM for flask
- [Werkzeug](https://werkzeug.palletsprojects.com/en/2.1.x/): For password hashing and other WSGI utilities
- [WTForms](https://wtforms.readthedocs.io/en/3.0.x/): For the login/registration forms
