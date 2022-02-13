import pytest
import urllib
import faker
from flask import url_for, session, get_flashed_messages
from task_manager.auths.tests.fixtures.sql_data import SQLS, ADMINISTRATOR, MANAGER, NEW_USER, EXECUTOR
from flask_login import current_user, login_user, logout_user

from task_manager.auths.models import Role, User

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'psw1': 123456,
            'psw2': 123456}


def test_url_logout(client, db):
    response = client.get(url_for('users.log_out'))
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert response.status_code == 302
    assert parsed.path == url_for('users.login')
    assert msg[0] == 'Please log in to access this page.'

    response = client.post(url_for('users.log_out'), data='')
    assert response.status_code == 405


def test_logged_url_logout(app, authenticated_client, db):
    assert current_user.is_authenticated
    response = authenticated_client.open(url_for('users.log_out'), method="GET")
    parsed = urllib.parse.urlparse(response.location)
    assert not current_user.is_authenticated
    assert response.status_code == 302
    assert parsed.path == url_for('main.index')
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


def test_url_login(app, db, client, faker):
    response = client.get(url_for('users.login'))
    assert response.status_code == 200
    response = client.post(url_for('users.login'),
                           data={'email': faker.ascii_email(),
                                 'psw': '1234'})
    msg = get_flashed_messages()
    assert response.status_code == 200
    assert b'Authorization' in response.data



