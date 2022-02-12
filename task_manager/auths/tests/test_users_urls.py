import pytest
import urllib
from flask import url_for

from task_manager.auths.models import Role, User

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'password': 123456}


def test_url_register(client):
    response = client.get(url_for('users.register'))
    assert response.status_code == 200
    response = client.post(url_for('users.register'), data=NEW_USER)
    assert response.status_code == 200

def test_url_login(client):
    response = client.get(url_for('users.login'))
    assert response.status_code == 200
    response = client.post(url_for('users.login'), data=NEW_USER)
    assert response.status_code == 200

def test_url_logout(client):
    response = client.get(url_for('users.log_out'))
    assert response.status_code == 302
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for('users.log_out'), data=NEW_USER)
    assert response.status_code == 405