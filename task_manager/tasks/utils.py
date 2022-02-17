import logging
from datetime import date

from task_manager.statuses.models import Status
from task_manager.tags.models import Tag
from task_manager.tasks.models import Task, Plan, IntermediateTaskTag
from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission  # noqa 402


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
        if step['actual_start'] and not step['actual_end_date']:
            status = Status.query.filter_by(id=step['status_id']).one()
            status_name = status['name']
            return status_name
    return 'No status'