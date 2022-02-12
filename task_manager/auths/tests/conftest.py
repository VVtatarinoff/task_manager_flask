import os
import tempfile

import pytest
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from task_manager import create_app


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
    with app.app_context():
        migrate = Migrate(app, db)
        upgrade()
    return db

@pytest.fixture(scope='session')
def _db(app):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    db = SQLAlchemy(app)
    return db
