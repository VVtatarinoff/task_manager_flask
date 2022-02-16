import logging
from datetime import datetime, date

from flask import Blueprint, redirect, url_for, request, flash, render_template, session
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
    choices = extract_choices()
    steps = session.get('steps', [])
    if not request.form and steps:
        session['steps'] = []
    form = CreateTask(**choices)
    if form.add_step.data:
        if msg := get_error_for_step(form):
            flash(msg, "warning")
        else:
            step_id = int(form.step_name.data)
            status = Status.query.filter_by(id=step_id).one()
            step_name = status.name
            step = {'step_id': step_id,
                    'step_name': step_name,
                    'start': form.start_step_date.data.toordinal(),
                    'end': form.planned_step_end.data.toordinal()}
            session['steps'] = steps + [step]
            form.step_name.data = None
            form.start_step_date.data = form.start_step_date.raw_data = None
            form.planned_step_end.data = form.planned_step_end.raw_data = None
    context = dict()
    context['form'] = form
    context['title'] = 'Create task'
    context['steps'] = session['steps']

    return render_template('tasks/task_creation.html', **context)


def extract_choices():
    choices =dict()
    executors = User.query.filter(User.role_id.in_([1, 2])).all()
    choices['executors'] = [(None, '           ')] + \
                     list(map(lambda x: (x.id, f"{x.first_name} {x.last_name}"), executors))
    tags = Tag.query.all()
    choices['tags'] = [(None, '           ')] + list(map(lambda x: (x.id, x.name), tags))
    statuses = Status.query.all()
    choices['step_names'] = [(None, '           ')] + list(map(lambda x: (x.id, x.name), statuses))
    return choices


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
    if end < start:
        return "Start date greater than deadline"
    if start < date.today():
        return "The start date is in the past"
    return False
