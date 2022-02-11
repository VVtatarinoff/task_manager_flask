import os
import tempfile

import pytest
import pytest_flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

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
def _db(app):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    db = SQLAlchemy(app)
    return db

"""
@pytest.fixture
def client(app):
    #db_fd, db_path = tempfile.mkstemp()
    #app = create_app({'TESTING': True, 'DATABASE': db_path})

    with app.app_context():
        with app.test_client() as client:
            db = SQLAlchemy(app)
            yield client
"""