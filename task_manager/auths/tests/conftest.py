import logging
import os
import tempfile

import pytest
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from task_manager import create_app
from flask_login import current_user, login_required, login_user, logout_user
from task_manager.auths.tests.fixtures.sql_data import SQLS, ADMINISTRATOR, MANAGER, NEW_USER, EXECUTOR
from task_manager.auths.models import User

logger = logging.getLogger(__name__)
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db(app):
    db = SQLAlchemy(app)
    with app.app_context():
        migrate = Migrate(app, db)
        upgrade()
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
    return db

@pytest.fixture
def authenticated_client(app, db):
    with app.test_request_context():
        cl = app.test_client()
        user = User.query.filter_by(email=EXECUTOR['email']).one()
        login_user(user)
        yield cl
        logout_user()


    '''
@pytest.fixture(scope='session')
def _db(app):

    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.

    db = SQLAlchemy(app)
    return db
'''