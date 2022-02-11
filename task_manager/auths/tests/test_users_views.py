import pytest
from flask import url_for

from task_manager.auths.models import Role, User

NEW_USER = {'name': 'test',
            'first_name': 'TEST',
            'last_name': 'TESTOFF',
            'email': 'test@mail.ru',
            'password': 123456}


#def test_registration(app, db_session):
    #response = client.get(url_for('register'))
#    user = User(name='test')
#    g=1


def test_post(app):
  #  response = client.get(url_for('users.register'))
 #   assert response.status_code == 200
    with app.test_request_context() as client:
        response = app.test_client().post(url_for('users.register'), data=NEW_USER)
    assert response.status_code == 200