import logging
from datetime import date

from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from task_manager import db
from task_manager.statuses.models import Status
from task_manager.tasks.models import Plan, IntermediateTaskTag, Task
from task_manager.tasks.session import SessionPlan

logger = logging.getLogger(__name__)


def create_tasks_list(tasks):
    task_list = []
    for task in tasks:
        task_view = dict()
        task_view['id'] = task.id
        task_view['name'] = task.name
        task_view['actual_end_date'] = task.actual_end_date
        task_view['planned_start'] = task.start_date
        task_view['planned_end'] = task.planned_end_date
        task_view['actual_start_date'] = task.actual_start_date
        task_view['on_review'] = task.post_to_review
        task_view['started'] = True
        task_view['finished'] = False
        steps = Plan.query.filter_by(task_id=task.id).all()
        if task_view['actual_end_date']:
            task_view['status'] = 'closed'
            task_view['finished'] = True
        elif not task_view['actual_start_date']:
            task_view['status'] = 'not started'
            task_view['started'] = False
        elif task.post_to_review:
            task_view['status'] = 'posted for review'
        else:
            task_view['status'] = get_current_status(steps)
        task_view['manager'] = task.manager_user.name
        task_view['executor'] = task.executor_user.name
        task_view['overdue'] = date.today() > task_view['planned_end']
        task_list += [task_view]
    return task_list


def get_current_status(steps):
    for step in steps:
        if step.actual_start and not step.actual_end_date:
            status = Status.query.filter_by(id=step.status_id).one()
            status_name = status.name
            return status_name
    return 'No status'


def upload_task(form):
    manager_id = current_user.id
    executor_id = form.executor.data
    task_name = form.task_name.data
    task_description = form.description.data
    steps = SessionPlan().plan
    task_start = sorted(list(map(lambda x: x['start_date'], steps)))[0]
    task_planned_end = sorted(list(map(lambda x: x['planned_end'], steps)))[0]
    task = Task(name=task_name, description=task_description,
                manager_id=manager_id, executor_id=executor_id,
                start_date=task_start, planned_end_date=task_planned_end)
    try:
        db.session.add(task)
        db.session.flush()
        id = task.id
        for step in steps:
            plan_item = Plan(start_date=step['start_date'],
                             planned_end=step['planned_end'],
                             status_id=step['status_id'],
                             task_id=id,
                             executor_id=executor_id)
            db.session.add(plan_item)
        for tag in form.tags.data:
            interlink = IntermediateTaskTag(
                task_id=id,
                tag_id=int(tag)
            )
            db.session.add(interlink)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def get_error_modifing_task(task):
    msg = ''
    if task.actual_end_date:
        msg = "Could not delete or change the finished task"
    if task.manager_user != current_user and (
            not current_user.is_administrator()):
        msg = "Only owner of the task could delete or change it"
    return msg
