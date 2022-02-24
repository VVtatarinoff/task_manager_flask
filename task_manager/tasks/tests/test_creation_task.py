from datetime import date

from flask import url_for, session
from flask_login import current_user

import pytest

from task_manager.database.development_sql_fill import MANAGER
from task_manager.tasks.forms import CreateTask
from task_manager.tasks.session import SessionPlan


@pytest.mark.parametrize('page', ['tasks.create_task'])
def test_authorized_manager_add_step(db_task, client, page):
    client.post(url_for('users.login'),
                data={'email': MANAGER['email'],
                      'psw': MANAGER['password']})
    assert current_user.is_authenticated
    _ = client.post(
        url_for(page), data={
            'status_name': 1,
            'start_date': date.today(),
            'planned_end': date.today(),
            'add_step': True
        })
    session_data = SessionPlan(form=CreateTask())
