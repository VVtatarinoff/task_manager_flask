import logging

import pytest
import urllib
from flask import url_for, get_flashed_messages
from flask_login import current_user

from task_manager.tasks.models import Task
from task_manager.tasks.tasks import TITLES
from task_manager.database.development_sql_fill import (
    EXECUTOR, MANAGER)

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('page', ['tasks.show_tasks_list',
                                  'tasks.create_task',
                                  'tasks.show_task_detail',
                                  'tasks.update_task',
                                  'tasks.delete_task'])
def test_show_tasks_list_unlogged_get(db_task, client, page):
    response = client.get(
        url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')


@pytest.mark.parametrize('page', ['tasks.show_tasks_list',
                                  'tasks.show_task_detail'])
def test_show_tasks_list_unlogged_post405(db_task, client, page):
    response = client.post(url_for(page, id=1))
    assert response.status_code == 405


@pytest.mark.parametrize('page', ['tasks.create_task',
                                  'tasks.update_task',
                                  'tasks.delete_task'])
def test_show_tasks_list_unlogged_post302(db_task, client, page):
    response = client.post(url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')


@pytest.mark.parametrize('page', ['tasks.create_task',
                                  'tasks.delete_task',
                                  'tasks.update_task'])
def test_show_tasks_list_unthorized_post(db_task, client, page):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    _ = get_flashed_messages()
    assert current_user.is_authenticated
    response = client.get(
        url_for('tasks.show_tasks_list'))
    response = client.post(url_for(page, id=1))
    assert response.status_code == 403


def test_show_task_list_authorized(app, db_task, client):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    _ = get_flashed_messages()
    assert current_user.is_authenticated
    response = client.get(
        url_for('tasks.show_tasks_list'))
    assert response.status_code == 200
    assert bytes(TITLES['list'], 'utf-8') in response.data
    tasks_count = Task.query.count()
    lines = response.data.count(b'</tr')
    assert lines == tasks_count


@pytest.mark.parametrize('page_info', [('tasks.create_task', TITLES['create']),
                                       ('tasks.update_task', TITLES['update'])])
def test_authorized_manager_get(db_task, client, page_info):
    page, title = page_info
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    _ = get_flashed_messages()
    assert current_user.is_authenticated
    response = client.get(
        url_for(page, id=1))
    _ = get_flashed_messages()
    assert response.status_code == 200
    assert bytes(title, 'utf-8') in response.data
