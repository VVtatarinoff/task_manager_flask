import logging
import faker

import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from flask_login import current_user

from task_manager.tags.models import Tag  # noqa 401
from task_manager.database.development_sql_fill import (
    EXECUTOR, MANAGER, TAGS)

logger = logging.getLogger(__name__)
fake = faker.Faker()
NEW_TAG = {'name': fake.pystr(min_chars=5, max_chars=20),
           'description': fake.street_address()}


@pytest.mark.parametrize('page', ['tags.show_tags_list',
                                  'tags.show_tag_detail'])
def test_unlogged_get_pages(app, db_tag, client, page):
    response = client.get(
        url_for(page, id=1))
    assert response.status_code == 302
    msg = get_flashed_messages()
    assert msg[0] == 'Please log in to access this page.'
    parsed = urllib.parse.urlparse(response.location)
    assert parsed.path == url_for('users.login')
    response = client.post(url_for(page, id=1))
    assert response.status_code == 405


def test_authorized_show_tags_list(app, db_tag, client):
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


@pytest.mark.parametrize('page', ['tags.create_tag',
                                  'tags.edit_tag'])
def test_unlogged_get_post_page(db_tag, client, page):
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


@pytest.mark.parametrize('page', ['tags.create_tag',
                                  'tags.edit_tag'])
def test_unauthorized_get_post_page(db_tag, client, page):
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


def test_authorized_create_tag(db_tag, client):
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
    db_tag.session.commit()
    assert tags_count == Tag.query.count()
    assert response.status_code == 302
    assert parsed.path == url_for('tags.show_tags_list')
    assert msg[0] == f'Tag {NEW_TAG["name"]} created'


@pytest.mark.parametrize('tag_detail', TAGS)
def test_authorised_show_tag_detail(db_tag, client, tag_detail):
    tag = Tag.query.filter_by(name=tag_detail['name']).one()
    client.post(url_for('users.login'),
                data={'email': EXECUTOR['email'],
                      'psw': EXECUTOR['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(url_for('tags.show_tag_detail', id=tag.id))
    assert response.status_code == 200
    assert b'Tag detail' in response.data
    assert bytes(tag.name, 'utf-8') in response.data
    assert bytes(tag.description, 'utf-8') in response.data


@pytest.mark.parametrize('tag_detail', TAGS)
def test_authorized_edit_tag_get(db_tag, client, tag_detail):
    tag = Tag.query.filter_by(name=tag_detail['name']).one()
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    _ = get_flashed_messages()
    response = client.get(
        url_for('tags.edit_tag', id=tag.id))
    assert response.status_code == 200
    assert bytes(f'Edit tag #{tag.name}', 'utf-8') in response.data
    assert bytes(tag.name, 'utf-8') in response.data
    assert bytes(tag.description, 'utf-8') in response.data


@pytest.mark.parametrize('tag_detail', TAGS)
def test_authorized_edit_tag_post(db_tag, client, tag_detail):
    tag = Tag.query.filter_by(name=tag_detail['name']).one()
    id = tag.id
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    response = client.get(
        url_for('tags.edit_tag', id=tag.id))
    assert response.status_code == 200
    new_name = tag.name[:15] + 'test'
    new_description = 'test' + tag.description + 'test'
    tags_count = Tag.query.count()
    response = client.post(url_for('tags.edit_tag', id=tag.id),
                           data={'name': new_name,
                                 'description': new_description},
                           )
    assert response.status_code == 302
    tag = Tag.query.filter_by(id=id).one()
    msg_expected = f'Details of tag #{tag.name} have been updated.'
    msg_received = get_flashed_messages()
    assert msg_expected in msg_received
    assert tags_count == Tag.query.count()
    assert tag.name == new_name
    assert tag.description == new_description
