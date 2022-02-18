#!/usr/bin/env python
from pathlib import Path

from flask_migrate import upgrade, Migrate

from task_manager import create_app, db
from task_manager.database.development_sql_fill import SQLS

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent

app = create_app('development')


if __name__ == '__main__':
    with app.app_context():
        migrate = Migrate(app, db)  # noqa 481
        directory = BASE_DIR / 'migrations'
        upgrade(directory=directory)
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
