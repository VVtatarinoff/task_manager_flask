#!/usr/bin/env python
import logging
from pathlib import Path

from flask_migrate import upgrade, Migrate  # noqa 401

from task_manager import create_app
from task_manager.database.development_sql_fill import SQLS

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent

app = create_app('development')

from task_manager import db # noqa 402

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logger.debug(f'init db. app: {app}, db: {db}')
    with app.app_context():
        # migrate = Migrate(app, db)  # noqa 481
        # directory = BASE_DIR / 'migrations'
        # upgrade(directory=directory)
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
