import werkzeug
from flask import url_for
from flask_login import current_user

from task_manager.auths.users import permission_required


def test_permission_required(app, db_app, client, user_permission):
    email, password, permission_name, permission_value = user_permission
    decorator = permission_required(permission_name)
    client.post(url_for('users.login'),
                data={'email': email,
                      'psw': password})
    assert current_user.is_authenticated
    try:
        decorator(bool)(True)
    except werkzeug.exceptions.Forbidden:
        assert not permission_value
    else:
        assert permission_value
