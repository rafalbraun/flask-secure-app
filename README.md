## Setup
$ mkdir flask-app
$ cd flask-app
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 app.py

## Setup database
$ source venv/bin/activate
$ export FLASK_APP=app
$ flask shell
>>> from app import db, User
>>> db.create_all()
>>> db.drop_all()

## Save requirements
pip freeze > requirements.txt

## Install requirements
pip install -r requirements.txt


## requires itsdangerous==2.0.1
https://stackoverflow.com/questions/74039971/importerror-cannot-import-name-timedjsonwebsignatureserializer-from-itsdange


