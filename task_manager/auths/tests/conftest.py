import logging
from pathlib import Path

import pytest
from flask_migrate import Migrate, upgrade

from task_manager import create_app, db
from task_manager.database.test_sql_data import (
    SQLS, ADMINISTRATOR, EXECUTOR, MANAGER)
from task_manager.auths.models import Permission

logger = logging.getLogger(__name__)
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent.parent

permission_mapping = [
    {(ADMINISTRATOR['email'], ADMINISTRATOR['password']): {
        Permission.REVIEW: True,
        Permission.EXECUTE: True,
        Permission.MANAGE: True,
        Permission.ADMINISTER: True}},
    {(EXECUTOR['email'], EXECUTOR['password']): {
        Permission.REVIEW: True,
        Permission.EXECUTE: True,
        Permission.MANAGE: False,
        Permission.ADMINISTER: False}},
    {(MANAGER['email'], MANAGER['password']): {
        Permission.REVIEW: True,
        Permission.EXECUTE: True,
        Permission.MANAGE: True,
        Permission.ADMINISTER: False}}]


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db_app(app):
    # db = SQLAlchemy(app)
    with app.app_context():
        migrate = Migrate(app, db)  # noqa 481
        directory = BASE_DIR / 'migrations'
        upgrade(directory=directory)
        with db.engine.connect() as con:
            for sql in SQLS:
                con.execute(sql)
        yield db


def get_user_permission_choices():
    choices = []
    for user in permission_mapping:
        for credetentials, permissions in user.items():
            email, password = credetentials
            for permission_name, permission_value in permissions.items():
                choices += [
                    (email, password, permission_name, permission_value)]
    return choices


permission_choices = get_user_permission_choices()


@pytest.fixture(params=permission_choices, scope='session')
def user_permission(request):
    return request.param
