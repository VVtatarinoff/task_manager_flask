import logging
import faker


import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from flask_login import current_user

from task_manager.tags.models import Tag    # noqa 401
from task_manager.database.test_sql_data import EXECUTOR, MANAGER

logger = logging.getLogger(__name__)
fake = faker.Faker()
NEW_TAG = {'name': fake.pystr(min_chars=5, max_chars=20),
           'description': fake.street_address()}


def test_unauthorized_show_tags_list(app, db_app, client):
    response = client.get(
        url_for('tags.show_tags_list'))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for('tags.show_tags_list'))
    assert response.status_code == 405


def test_authorized_show_tags_list(app, db_app, client):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    _ = get_flashed_messages()
    assert current_user.is_authenticated
    response = client.get(
        url_for('tags.show_tags_list'))
    assert response.status_code == 200
    assert b'Tags' in response.data
    tags_count = Tag.query.count()
    lines = response.data.count(b'</tr')
    assert lines == tags_count


def test_unlogged_create_tag(db_app, client):
    response = client.get(
        url_for('tags.create_tag'))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for('tags.create_tag'))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')


def test_unautorized_create_tag(db_app, client):
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(
        url_for('tags.create_tag'))
    assert response.status_code == 403
    response = client.post(url_for('tags.create_tag'))
    assert response.status_code == 403


def test_authorized_create_tag(db_app, client):
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(
        url_for('tags.create_tag'))
    assert response.status_code == 200
    assert b'Create tag' in response.data
    tags_count = Tag.query.count()
    response = client.post(
        url_for('tags.create_tag'), data=NEW_TAG)
    assert response.status_code == 302
    parsed = urllib.parse.urlparse(response.location)
    msg = get_flashed_messages()
    assert tags_count + 1 == Tag.query.count()
    new_tag = Tag.query.filter_by(name=NEW_TAG['name']).one()
    assert new_tag.creation_date
    assert new_tag.description == NEW_TAG['description']
    Tag.query.filter_by(name=NEW_TAG['name']).delete()
    db_app.session.commit()
    assert tags_count == Tag.query.count()
    assert response.status_code == 302
    assert parsed.path == url_for('tags.show_tags_list')
    assert msg[0] == f'Tag {NEW_TAG["name"]} created'
