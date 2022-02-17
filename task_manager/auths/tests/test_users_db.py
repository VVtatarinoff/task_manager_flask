import urllib

import werkzeug

from flask import url_for, get_flashed_messages
from flask_login import current_user, login_user

from task_manager.auths.models import User
from task_manager.database.development_sql_fill import (
    ADMINISTRATOR, EXECUTOR, MANAGER)
from task_manager.auths.users import (
    permission_required, self_or_admin_required)


def test_permission_required(db_app, user_permission):
    email, password, permission_name, permission_value = user_permission
    decorator = permission_required(permission_name)
    user = User.query.filter_by(email=email).one()
    login_user(user)
    assert current_user.is_authenticated
    try:
        decorator(bool)(True)
    except werkzeug.exceptions.Forbidden:
        assert not permission_value
    else:
        assert permission_value


def test_admin_self_or_admin_required(app, db_app, client):
    logged_user = User.query.filter_by(email=ADMINISTRATOR['email']).one()
    login_user(logged_user)
    assert current_user.is_authenticated
    msg = 'access denyied test'
    decorator = self_or_admin_required(msg)
    assert isinstance(decorator(bool)(ADMINISTRATOR['name']), bool)
    assert isinstance(decorator(bool)(EXECUTOR['name']), bool)
    assert isinstance(decorator(bool)(MANAGER['name']), bool)


def test_user_self_or_admin_required(app, db_app, client):
    logged_user = User.query.filter_by(email=EXECUTOR['email']).one()
    login_user(logged_user)
    assert current_user.is_authenticated
    msg = 'access denied test'
    decorator = self_or_admin_required(msg)
    response = decorator(bool)(ADMINISTRATOR['name'])
    parsed = urllib.parse.urlparse(response.location)
    assert msg == get_flashed_messages()[0]
    assert parsed.path == url_for('main.index')
    assert isinstance(decorator(bool)(EXECUTOR['name']), bool)
    response = decorator(bool)(MANAGER['name'])
    parsed = urllib.parse.urlparse(response.location)
    assert msg == get_flashed_messages()[0]
    assert parsed.path == url_for('main.index')
