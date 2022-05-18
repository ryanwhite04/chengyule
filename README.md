
# Setting up development environment

## Check python version
Use at least python 3.9 (3.10 should work too)

to check what version you are using you can use 

```python --version```

or

```python3 --version```

If you are using ubuntu, the default repo only shows up to 3.8, but you can follow these instructions to get 3.9

```sudo apt update```
```sudo apt install software-properties-common```
```sudo add-apt-repository ppa:deadsnakes/ppa```
```sudo apt install python3.9```

then check it worked

```python3.9 --version```

should return 

```Python 3.9.1+```

## Set up and activate a virtual environment

```python3.9 -m venv venv```
```. ./venv/bin/activate```

## Install python dependencies

*This command should only be run once the environment has been activated*
*You should see (venv) at the start of your command line*

```pip install -r requirements.txt```

## Install heroku

This is only needed if you want to push the site so that it goes live
You can still work on it locally without this, and this isn't necessary for the assignment it's just for fun

You can try following [Heroku's Guide](https://devcenter.heroku.com/articles/getting-started-with-python#set-up) but that didn't work for me because i'm using WSL2 on windows and it throws an error.

If you get an error too, you can just try
```curl https://cli-assets.heroku.com/install-ubuntu.sh | sh```
but this wont autoupdate or anything
also, here is a [link](https://cli-assets.heroku.com/install.sh) to the script if you want to take a look before installing it

# Running Locally

## Static website
If you just want to mess around with the "selection-puzzle" web component and add some features, you don't need to run flask or anything.
You can just ```cd``` into the ```static``` directory and run ```python -m http.server``` and visit [localhost:8000](http://localhost:8000) in your browser

Right now I'm using google's [Lit](https://lit.dev/) web-component library
It's really nice and makes great reusable web-components at only 5KB.
Since this isn't on the allowed list of technologies for this assignment it will have to be removed before submission though.
I'll probably just swap to using the browsers inbuilt [Custom Elements](https://web.dev/custom-elements-v1/) which is just missing the automatic getter/setter stuff, the tagged template literal html library and some lifecycle methods, but it's still really good.

I've also linked this static website to netlify so once main is pushed to the github repo you can visit it at [chengyu.netlify.app](https://chengyu.netlify.app)

## Flask Website

If you want to work on the backend, you'll have to run the flask app instead.

```flask run```

By setting the FLASK_ENV environment variable to "development" it means the server resets when you make changes to files so you don't have to keep restarting the server all the time which is a pain

TODO: This can later be put into a .env file and loaded automatically using [these instructions](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

I think it's as simple as 

```pip install python-dotenv```
```pip freeze > requirements.txt```
```echo "FLASK_ENV=development" > .env"```

and should be good to go, and .env is already ignored by .gitignore

## Heroku Local

If you installed heroku, you can run it through that too using 

```heroku local```

It just looks in the *Procfile* and sees "web: gunicorn app:app" and runs the webapp using gunicorn which is in python dependancies
I don't see any benefit yet to using this over ```flask run``` though so I wouldn't worry about it

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

# Database

Make sure you have the packages required

```pip install -r requirements.txt```

This will install Flask-SQLAlchemy and Flask-Migrate if you don't have them already

Initialize database

```DATABASE_URL=sqlite:///app.db flask db init```
```DATABASE_URL=sqlite:///app.db flask db migrate```

DATABASE_URL is passed in manually for now but we can put it in a .env later

# Testing

```python test.py```

To play around in shell, you can run

```
python
>>> from test import UserModelCase, db, User, Play, Game
>>> umc = UserModelCase()
>>> umc.setUp()
>>> games, users = umc.populate()
(<Game a>, <Game b>, <Game c>)
>>> User.query.all()
[<User a>, <User b>, <User c>]
```

# New Stuff

>>>python -m unittest test.test_modules.py

# Installing Postgresql

https://devcenter.heroku.com/articles/heroku-postgresql