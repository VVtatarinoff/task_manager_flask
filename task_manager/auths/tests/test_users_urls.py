import logging

import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from task_manager.database.development_sql_fill import (
    ADMINISTRATOR, MANAGER, EXECUTOR)
from flask_login import current_user
from task_manager.auths.models import User

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
    new_user = User.query.filter_by(name=NEW_USER['name']).one()
    assert new_user.role_id
    assert new_user.creation_date
    assert new_user.last_seen
    assert new_user.password_hash != NEW_USER['psw1']
    User.query.filter_by(name=NEW_USER['name']).delete()
    db_app.session.commit()
    assert users_count == User.query.count()
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
    response = client.get(
        url_for('users.get_user_list') + '?Executor=&Administrator=&Manager=')
    assert response.status_code == 200
    assert b'Users' in response.data
    users_count = User.query.count()
    lines = response.data.count(b'</tr')
    assert lines == users_count


@pytest.mark.parametrize('qry', [('?Executor=&Administrator=&Manager=', 3),
                                 ('?Executor=&Administrator=', 2),
                                 ('?Executor=&Manager=', 2),
                                 ('?Manager=&Administrator=', 2),
                                 ('?Executor=', 1),
                                 ('?Manager=', 1),
                                 ('?Administrator=', 1),
                                 ('', 0)])
def test_get_user_list_filtered(app, db_app, client, qry):
    response = client.get(
        url_for('users.get_user_list') + qry[0])
    assert response.status_code == 200
    users_count = qry[1]
    lines = response.data.count(b'</tr')
    assert lines == users_count


@pytest.mark.parametrize('user', [ADMINISTRATOR, EXECUTOR, MANAGER])
def test_profile_unauthorized(app, db_app, client, user):
    response = client.post(url_for('users.show_profile', username=user['name']))
    assert response.status_code == 405
    response = client.get(url_for('users.show_profile', username=user['name']))
    assert response.status_code == 302


@pytest.mark.parametrize('user', [ADMINISTRATOR, EXECUTOR, MANAGER])
def test_profile_authorized(app, db_app, client, user):
    _user = User.query.filter_by(name=user['name']).one()
    client.post(url_for('users.login'),
                data={'email': user['email'],
                      'psw': user['password']})
    response = client.get(url_for('users.show_profile', username=user['name']))
    assert response.status_code == 200
    assert b'User profile' in response.data
    assert bytes(_user.name, 'utf-8') in response.data
    assert bytes(_user.email, 'utf-8') in response.data
    assert bytes(_user.first_name, 'utf-8') in response.data
    assert bytes(_user.last_name, 'utf-8') in response.data
    assert bytes(_user.role.name, 'utf-8') in response.data


@pytest.mark.parametrize('user', [ADMINISTRATOR, EXECUTOR, MANAGER])
def test_profile_edit_unauthorized(app, client, user):
    response = client.get(url_for('users.edit_profile', username=user['name']))
    msg = get_flashed_messages()
    parsed = urllib.parse.urlparse(response.location)
    assert msg[0] == 'Please log in to access this page.'
    assert response.status_code == 302
    assert parsed.path == url_for('users.login')
    response = client.post(url_for('users.edit_profile', username=user['name']))
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    assert response.status_code == 302
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')


@pytest.mark.parametrize('user', [EXECUTOR, MANAGER])
def test_profile_edit_authorized_get(app, client, user):
    _user = User.query.filter_by(name=user['name']).one()
    client.post(url_for('users.login'),
                data={'email': user['email'],
                      'psw': user['password']})
    response = client.get(url_for('users.edit_profile', username=user['name']))
    title = f"Edit profile of {user['name']}"
    assert response.status_code == 200
    assert bytes(title, 'utf-8') in response.data
    assert bytes(_user.name, 'utf-8') in response.data
    assert bytes('value="' + _user.name, 'utf-8') not in response.data
    assert bytes('value="' + _user.first_name, 'utf-8') in response.data
    assert bytes('value="' + _user.last_name, 'utf-8') in response.data
    assert bytes('value="' + _user.email, 'utf-8') not in response.data
    assert bytes('>' + _user.role.name + '<', 'utf-8') not in response.data


@pytest.mark.parametrize('user', [EXECUTOR, MANAGER])
def test_profile_edit_authorized_post(app, client, user):
    _user = User.query.filter_by(name=user['name']).one()
    id = _user.id
    client.post(url_for('users.login'),
                data={'email': user['email'],
                      'psw': user['password']})
    new_first_name = _user.first_name + 'test'
    new_last_name = _user.last_name + 'test'
    new_name = _user.name + 'test'
    new_email = 'test' + _user.email
    old_role_id = _user.role_id
    new_role_id = 3
    location = "TEST"
    users_count = User.query.count()
    response = client.post(url_for('users.edit_profile', username=user['name']),
                           data={'first_name': new_first_name,
                                 'last_name': new_last_name,
                                 'location': location,
                                 'name': new_name,
                                 'role_id': new_role_id,
                                 'email': new_email}, )

    msg_expected = f'Profile of {_user.name} has been updated.'
    msg_received = get_flashed_messages()
    _user = User.query.filter_by(id=id).one()
    assert msg_expected in msg_received
    assert response.status_code == 302
    assert users_count == User.query.count()
    assert _user.location == location
    assert _user.first_name == new_first_name
    assert _user.last_name == new_last_name
    assert _user.name == user['name']
    assert _user.email == user['email']
    assert _user.role_id == old_role_id


@pytest.mark.parametrize('user', [ADMINISTRATOR, ])
def test_profile_edit_administrator_get(app, client, user):
    _user = User.query.filter_by(name=user['name']).one()
    client.post(url_for('users.login'),
                data={'email': user['email'],
                      'psw': user['password']})
    response = client.get(url_for('users.edit_profile', username=user['name']))
    assert bytes('value="' + _user.email, 'utf-8') in response.data
    assert bytes('>' + _user.role.name + '<', 'utf-8') in response.data


@pytest.mark.parametrize('user', [ADMINISTRATOR, ])
def test_profile_edit_administrator_post(app, client, user):
    _user = User.query.filter_by(name=MANAGER['name']).one()
    id = _user.id
    client.post(url_for('users.login'),
                data={'email': user['email'],
                      'psw': user['password']})
    new_first_name = _user.first_name + 'test'
    new_last_name = _user.last_name + 'test'
    new_name = _user.name + 'test'
    new_email = 'test' + _user.email
    old_role_id = _user.role_id
    new_role_id = old_role_id + 1
    location = "TEST"
    users_count = User.query.count()
    response = client.post(url_for('users.edit_profile', username=_user.name),
                           data={'first_name': new_first_name,
                                 'last_name': new_last_name,
                                 'location': location,
                                 'name': new_name,
                                 'role': new_role_id,
                                 'email': new_email}, )
    _user = User.query.filter_by(id=id).one()
    msg_expected = f'Profile of {_user.name} has been updated.'
    msg_received = get_flashed_messages()
    assert msg_expected in msg_received
    assert response.status_code == 302
    assert users_count == User.query.count()
    assert _user.location == location
    assert _user.first_name == new_first_name
    assert _user.last_name == new_last_name
    assert _user.name == MANAGER['name']
    assert _user.email == new_email
    assert _user.role_id == new_role_id
