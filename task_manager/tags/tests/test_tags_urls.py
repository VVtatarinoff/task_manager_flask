import logging

import pytest  # noqa 401
import urllib
from flask import url_for, get_flashed_messages
from task_manager.tags.models import Tag    # noqa 401
from task_manager.database.test_sql_data import TAG_QNTY, SQL_TAGS

logger = logging.getLogger(__name__)


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

