import logging
from datetime import date
from operator import and_

from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from task_manager import db
from task_manager.statuses.models import Status
from task_manager.tasks.forms import CreateTask
from task_manager.tasks.models import Plan, IntermediateTaskTag, Task

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


def get_plan_from_form(form: CreateTask):
    steps = []
    for id in form.ids:
        step = dict()
        step['start_date'] = form.__dict__[f'start_date_{id}'].data
        step['plan_id'] = int(id)
        step['planned_end'] = form.__dict__[f'planned_end_{id}'].data
        step['status_id'] = form.__dict__[f'status_id_{id}'].data
        steps.append(step)
    return steps


def upload_task(form):
    manager_id = current_user.id
    executor_id = form.executor.data
    task_name = form.task_name.data
    task_description = form.description.data
    steps = get_plan_from_form(form)
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


def update_tags(task, form):
    existed_tags = set(map(lambda x: x.id, task.tags))
    form_tags = set(map(int, form.tags.raw_data))
    del_tags = existed_tags - form_tags
    add_tags = form_tags - existed_tags
    for tag in (del_tags | add_tags):
        if tag in del_tags:
            interlink = IntermediateTaskTag.query.filter(
                and_(IntermediateTaskTag.task_id == task.id,
                     IntermediateTaskTag.tag_id == tag)).one()
            db.session.delete(interlink)
        else:
            interlink = IntermediateTaskTag(
                task_id=task.id,
                tag_id=tag
            )
            db.session.add(interlink)


def change_task(task, form):
    try:
        task.name = form.task_name.data
        task.description = form.description.data
        db.session.add(task)
        update_tags(task, form)
        existed_steps = set(map(lambda x: x.id, task.plan.all()))
        form_steps = set(map(int, form.ids))
        del_steps = existed_steps - form_steps
        for step in del_steps:
            db.session.delete(Plan.query.filter_by(id=step).one())
        for step in form_steps:
            # step_attr = {
            #     'status_id': int(form.__dict__[f'status_id_{step}'].data),
            #     'start_date': form.__dict__[f'start_date_{step}'].data,
            #     'planned_end': form.__dict__[f'planned_end_{step}'].data,
            #     'task_id': task.id,
            #     'executor_id':
            #         form.__dict__[
            #             f'executor_id_{step}'].data or int(
            #             form.executor.data)}
            pass
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
