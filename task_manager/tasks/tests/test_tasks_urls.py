import logging

import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from flask_login import current_user

from task_manager.tasks.models import Task, Plan  # noqa 401
from task_manager.database.development_sql_fill import (
    EXECUTOR)

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('page', ['tasks.show_tasks_list'])
def test_show_tasks_list_unauthorized(db_task, client, page):
    response = client.get(
        url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for(page, id=1))
    assert response.status_code == 405


def test_show_task_list_authorized(app, db_task, client):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    _ = get_flashed_messages()
    assert current_user.is_authenticated
    response = client.get(
        url_for('tasks.show_tasks_list'))
    assert response.status_code == 200
    assert b'Tasks' in response.data
    tasks_count = Task.query.count()
    lines = response.data.count(b'</tr')
    assert lines == tasks_count
