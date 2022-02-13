import logging

import pytest
import urllib
import faker
from flask import url_for, session, get_flashed_messages
from task_manager.auths.tests.fixtures.sql_data import SQLS, ADMINISTRATOR, MANAGER, NEW_USER, EXECUTOR
from flask_login import current_user, login_user, logout_user

from task_manager.auths.models import Role, User

logger = logging.getLogger(__name__)

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'psw1': 123456,
            'psw2': 123456}


def test_url_logout(client, db):
    response = client.get(url_for('users.log_out'))
    logger.disabled = False
    logger.debug(f'logout test GET - not logged, response {response.status_code}')
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert response.status_code == 302
    assert parsed.path == url_for('users.login')
    assert msg[0] == 'Please log in to access this page.'

    response = client.post(url_for('users.log_out'), data='')
    assert response.status_code == 405


def test_logged_url_logout(app, client, db):
    client.post(url_for('users.login'),
                           data={'email': EXECUTOR['email'],
                                 'psw': EXECUTOR['password']})
    assert current_user.is_authenticated
    logger.disabled = False
    logger.debug(f'logout test GET - logged, before - current_user {current_user}')
    response = client.open(url_for('users.log_out'), method="GET")
    logger.debug(f'logout test GET - logged, after -current_user {current_user}')
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('main.index')
    assert not current_user.is_authenticated
    assert response.status_code == 302
    assert current_user.is_anonymous


def test_url_register(client, db):
    response = client.get(url_for('users.register'))
    assert response.status_code == 200
    response = client.post(url_for('users.register'), data=NEW_USER)
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert response.status_code == 302
    assert parsed.path == url_for('users.login')
    assert msg[0] == 'User registered'


def test_url_wrong_login(app, db, client, faker):
    response = client.get(url_for('users.login'))
    assert response.status_code == 200
    response = client.post(url_for('users.login'),
                           data={'email': faker.ascii_email(),
                                 'psw': '123456'})
    msg = get_flashed_messages()
    assert msg[0] == 'Invalid email or password.'
    assert response.status_code == 200
    assert b'Authorization' in response.data


def test_url_correct_login(app, db, client):
    response = client.post(url_for('users.login'),
                           data={'email': EXECUTOR['email'],
                                 'psw': EXECUTOR['password']})
    msg = get_flashed_messages()
    parsed = urllib.parse.urlparse(response.location)
    assert msg[0] == f"{EXECUTOR['name']} logged in"
    assert response.status_code == 302
    assert parsed.path == url_for('main.index')
    assert current_user.is_authenticated
    assert current_user.email == EXECUTOR['email']


