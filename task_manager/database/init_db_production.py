#!/usr/bin/env python
import os
from pathlib import Path

from flask_migrate import upgrade, Migrate

from task_manager import create_app, db
import task_manager.database.development_sql_fill as fill

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
SQLS = [
    "DELETE FROM roles",
    "INSERT INTO roles (name, default_flag, permissions)"
    " VALUES ('Executor','True','3')",
    "INSERT INTO roles (name, default_flag, permissions)"
    " VALUES ('Manager','False','7')",
    "INSERT INTO roles (name, default_flag, permissions)"
    " VALUES ('Administrator','False','255')"
]

if __name__ == '__main__':
    with app.app_context():
        migrate = Migrate(app, db)  # noqa 481
        directory = BASE_DIR / 'migrations'
        upgrade(directory=directory)
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
