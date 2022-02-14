import logging
import os

import pytest
from flask_migrate import Migrate, upgrade
from task_manager import create_app, db
from task_manager.auths.tests.fixtures.sql_data import SQLS

logger = logging.getLogger(__name__)
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db_app(app):
    # db = SQLAlchemy(app)
    with app.app_context():
        migrate = Migrate(app, db)      # noqa 481
        upgrade()
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
        yield db
