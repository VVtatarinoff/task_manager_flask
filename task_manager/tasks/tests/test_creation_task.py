from flask import url_for
from flask_login import current_user

import pytest

from task_manager.database.development_sql_fill import MANAGER


@pytest.mark.parametrize('page', ['tasks.create_task'])
def test_authorized_manager_post(db_task, client, page):
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    _ = client.post(
        url_for(page, id=1))
