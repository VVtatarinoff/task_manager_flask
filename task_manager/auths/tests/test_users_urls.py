import pytest
import urllib
from flask import url_for

from task_manager.auths.models import Role, User

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'psw1': 123456,
            'psw2': 123456}

def test_url_logout(client,db):
    response = client.get(url_for('users.log_out'))
    assert response.status_code == 302
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for('users.log_out'), data=NEW_USER)
    assert response.status_code == 405


def test_url_register(client, db):
    response = client.get(url_for('users.register'))
    assert response.status_code == 200
    response = client.post(url_for('users.register'), data=NEW_USER)
    assert response.status_code == 302
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')


def test_url_login(app, db, client):
    response = client.get(url_for('users.login'))
    assert response.status_code == 200
    response = client.post(url_for('users.login'), data={'email': 'bla@gmail.com', 'password': '1234'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Authorization' in response.data
#    assert 'Invalid email or password' == app.session.get_flashed_messages()




