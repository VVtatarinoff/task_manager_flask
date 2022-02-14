import logging

import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from task_manager.auths.tests.fixtures.sql_data import (
    ADMINISTRATOR, MANAGER, EXECUTOR)
from flask_login import current_user
from task_manager.auths.models import User, Permission, Role

logger = logging.getLogger(__name__)

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'psw1': 123456,
            'psw2': 123456}


def test_url_logout(client, db_app):
    response = client.get(url_for('users.log_out'))
    logger.disabled = False
    logger.debug(f'logout test GET - not logged, '
                 f'response {response.status_code}')
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert response.status_code == 302
    assert parsed.path == url_for('users.login')
    assert msg[0] == 'Please log in to access this page.'

    response = client.post(url_for('users.log_out'), data='')
    assert response.status_code == 405


def test_logged_url_logout(app, client, db_app):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    assert current_user.is_authenticated
    logger.disabled = False
    logger.debug(f'logout test GET - logged, before -'
                 f' current_user {current_user}')
    response = client.open(url_for('users.log_out'), method="GET")
    logger.debug(f'logout test GET - logged, after - '
                 f'current_user {current_user}')
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('main.index')
    assert not current_user.is_authenticated
    assert response.status_code == 302
    assert current_user.is_anonymous


def test_url_register(client, db_app):
    response = client.get(url_for('users.register'))
    assert response.status_code == 200
    users_count = User.query.count()
    response = client.post(url_for('users.register'), data=NEW_USER)
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert users_count + 1 == User.query.count()
    User.query.filter_by(name=NEW_USER['name']).delete()
    db_app.session.commit()
    assert response.status_code == 302
    assert parsed.path == url_for('users.login')
    assert msg[0] == 'User registered'


def test_url_wrong_login(app, db_app, client, faker):
    response = client.get(url_for('users.login'))
    assert response.status_code == 200
    response = client.post(url_for('users.login'),
                           data={'email': faker.ascii_email(),
                                 'psw': '123456'})
    msg = get_flashed_messages()
    assert msg[0] == 'Invalid email or password.'
    assert response.status_code == 200
    assert b'Authorization' in response.data


@pytest.mark.parametrize('user', [ADMINISTRATOR, EXECUTOR, MANAGER])
def test_url_correct_login(app, db_app, client, user):
    response = client.post(url_for('users.login'),
                           data={'email': user['email'],
                                 'psw': user['password']})
    msg = get_flashed_messages()
    parsed = urllib.parse.urlparse(response.location)
    assert msg[0] == f"{user['name']} logged in"
    assert response.status_code == 302
    assert parsed.path == url_for('main.index')
    assert current_user.is_authenticated
    assert current_user.email == user['email']


def test_get_user_list(app, db_app, client):
    assert app.extensions['moment'].__name__ == 'moment'
    assert app.template_context_processors[None][1].__globals__[
               '__name__'] == 'flask_moment'
    response = client.get(url_for('users.get_user_list')+'?Executor=&Administrator=&Manager=')
    assert response.status_code == 200
    assert b'Users' in response.data
    users_count = User.query.count()
    lines = response.data.count(b'</tr')
    assert lines == users_count
