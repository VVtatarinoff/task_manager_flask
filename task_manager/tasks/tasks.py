import logging
from datetime import datetime

from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only

from task_manager.statuses.models import Status
from task_manager.tags.models import Tag
from task_manager.tasks.forms import CreateTask, EditTaskForm
from task_manager.tasks.models import Task, Plan

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402
from task_manager.auths.users import permission_required  # noqa 402

logger = logging.getLogger(__name__)


@tasks_bp.route('/tasks')
@login_required
def show_tasks_list():
    logger.disabled = False
    logger.debug(f'Task list request {request.method}, ars {request.args}')
    logger.debug(f'Task list request, tags = {list(Task.query.all())}')
    context = dict()
    context['title'] = 'Tasks'
    context['table_heads'] = ('ID', 'Name', 'Executor', 'Manager',
                              'Start_date', 'Planned end', 'Actual end',
                              'Current status', 'Creation date')
    tasks = []
    try:
        tasks = Task.query.all()
    except SQLAlchemyError as e:
        flash('Database error ', e)
    context['table_data'] = tasks
    return render_template('tasks/task_list.html', **context)


@tasks_bp.route('/task_detail/<int:id>')
@login_required
def show_task_detail(id):
    return redirect(url_for('main.index'))


@tasks_bp.route('/task_create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def create_task():
    executors = User.query.filter(User.role_id.in_([1,2])).all()
    executors_list = [(None, '           ')] + \
                     list(map(lambda x: (x.id, f"{x.first_name} {x.last_name}"), executors))
    if len(executors_list)<2:
        flash('No executors or managers in database ', 'error')
        return redirect(url_for("tasks.show_tasks_list"))
    tags = Tag.query.all()
    tags_list = [(None, '           ')]+list(map(lambda x: (x.id, x.name), tags))
    statuses = Status.query.all()
    status_list = [(None, '           ')]+list(map(lambda x: (x.id, x.name), statuses))
    form = CreateTask(executors=executors_list, tags=tags_list, step_names=status_list)
    if form.add_step:
        if msg := get_error_for_step(form):
            flash(msg)
        else:
            pass
    context = dict()
    context['form'] = form
    context['title'] = 'Create task'

    return render_template('tasks/task_creation.html', **context)

def get_error_for_step(form):
    step_id = form.step_name.data
    start = form.start_step_date.data
    end = form.planned_step_end.data
    if step_id == "None":
        return "Choose the step to include"
    if not start:
        return "Input start date"
    if not end:
        return "Input deadline"
    step_id = int(step_id)
    step = list(Status.query.filter_by(id=step_id).all())
    if len(step) == 0:
        return "No such status exists in database"
    if end > start:
        return "Start date less than deadline"
    today = datetime.today()
    if start < today:
        return "The start point is in the past"
    return False