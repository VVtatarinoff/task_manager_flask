import logging
import faker

import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from flask_login import current_user

from task_manager.statuses.models import Status
from task_manager.database.development_sql_fill import (
    EXECUTOR, MANAGER, STATUSES)

logger = logging.getLogger(__name__)
fake = faker.Faker()
NEW_STATUS = {'name': fake.pystr(min_chars=5, max_chars=20),
              'description': fake.street_address()}


@pytest.mark.parametrize('page', ['statuses.show_statuses_list',
                                  'statuses.show_status_detail'])
def test_unlogged_get_pages(app, db_status, client, page):
    response = client.get(
        url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for(page, id=1))
    assert response.status_code == 405


def test_authorized_show_statuses_list(app, db_status, client):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    _ = get_flashed_messages()
    assert current_user.is_authenticated
    response = client.get(
        url_for('statuses.show_statuses_list'))
    assert response.status_code == 200
    assert b'Statuses' in response.data
    statuses_count = Status.query.count()
    lines = response.data.count(b'</tr')
    assert lines == statuses_count


@pytest.mark.parametrize('page', ['statuses.create_status',
                                  'statuses.edit_status'])
def test_unlogged_get_post_page(db_status, client, page):
    response = client.get(
        url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')


@pytest.mark.parametrize('page', ['statuses.create_status',
                                  'statuses.edit_status'])
def test_unauthorized_get_post_page(db_status, client, page):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(
        url_for(page, id=1))
    assert response.status_code == 403
    response = client.post(url_for(page, id=1))
    assert response.status_code == 403


def test_authorized_create_status(db_status, client):
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(
        url_for('statuses.create_status'))
    assert response.status_code == 200
    assert b'Create status' in response.data
    statuses_count = Status.query.count()
    response = client.post(
        url_for('statuses.create_status'), data=NEW_STATUS)
    assert response.status_code == 302
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert statuses_count + 1 == Status.query.count()
    new_status = Status.query.filter_by(name=NEW_STATUS['name']).one()
    assert new_status.creation_date
    assert new_status.description == NEW_STATUS['description']
    Status.query.filter_by(name=NEW_STATUS['name']).delete()
    db_status.session.commit()
    assert statuses_count == Status.query.count()
    assert response.status_code == 302
    assert parsed.path == url_for('statuses.show_statuses_list')
    assert msg[0] == f'Status {NEW_STATUS["name"]} created'


@pytest.mark.parametrize('status_detail', STATUSES)
def test_authorised_show_status_detail(db_status, client, status_detail):
    status = Status.query.filter_by(name=status_detail['name']).one()
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(url_for('statuses.show_status_detail', id=status.id))
    assert response.status_code == 200
    assert b'Status detail' in response.data
    assert bytes(status.name, 'utf-8') in response.data
    assert bytes(status.description, 'utf-8') in response.data


@pytest.mark.parametrize('status_detail', STATUSES)
def test_authorized_edit_status_get(db_status, client, status_detail):
    status = Status.query.filter_by(name=status_detail['name']).one()
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(
        url_for('statuses.edit_status', id=status.id))
    assert response.status_code == 200
    assert bytes(f'Edit status {status.name}', 'utf-8') in response.data
    assert bytes(status.name, 'utf-8') in response.data
    assert bytes(status.description, 'utf-8') in response.data


@pytest.mark.parametrize('status_detail', STATUSES)
def test_authorized_edit_status_post(db_status, client, status_detail):
    status = Status.query.filter_by(name=status_detail['name']).one()
    id = status.id
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    response = client.get(
        url_for('statuses.edit_status', id=status.id))
    assert response.status_code == 200
    new_name = status.name[:15] + 'test'
    new_description = 'test' + status.description + 'test'
    statuses_count = Status.query.count()
    response = client.post(url_for('statuses.edit_status', id=status.id),
                           data={'name': new_name,
                                 'description': new_description},
                           )
    assert response.status_code == 302
    status = Status.query.filter_by(id=id).one()
    msg_expected = f'Details of status "{status.name}" have been updated.'
    msg_received = get_flashed_messages()
    assert msg_expected in msg_received
    assert statuses_count == Status.query.count()
    assert status.name == new_name
    assert status.description == new_description
