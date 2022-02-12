import os
import tempfile

import pytest
from flask_sqlalchemy import SQLAlchemy

from task_manager import create_app
from task_manager.sql_migr import migrate

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'password': 123456}


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def db(app):
    db = SQLAlchemy(app)
    migrate(app.config['SQLALCHEMY_DATABASE_URI'])
    return db

@pytest.fixture(scope='session')
def _db(app):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    db = SQLAlchemy(app)
    return db
