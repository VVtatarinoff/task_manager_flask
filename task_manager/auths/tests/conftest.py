import os
import tempfile

import pytest
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from task_manager import create_app
from task_manager.auths.tests.fixtures.sql_data import SQLS


NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'password': 123456}

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app


@pytest.fixture(scope='session')
def db(app):
    db = SQLAlchemy(app)
    # fixture_path = os.path.join(CURRENT_DIR, "fixtures/data.sql")
    with app.app_context():
        migrate = Migrate(app, db)
        upgrade()
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)


    return db

def log_in(app,db):
    pass


    '''
@pytest.fixture(scope='session')
def _db(app):

    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.

    db = SQLAlchemy(app)
    return db
'''