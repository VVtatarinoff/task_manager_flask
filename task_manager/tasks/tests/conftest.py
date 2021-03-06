import logging
from pathlib import Path

import pytest
from flask_migrate import Migrate, upgrade

from task_manager import create_app, db
from task_manager.database.development_sql_fill import (
    SQLS, )

logger = logging.getLogger(__name__)
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent.parent


@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def db_task(app):
    with app.app_context():
        migrate = Migrate(app, db)  # noqa 481
        directory = BASE_DIR / 'migrations'
        upgrade(directory=directory)
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
        yield db


def session_init(db_task):
    pass
