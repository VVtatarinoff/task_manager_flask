import logging
from datetime import datetime, date

from flask import Blueprint, redirect, url_for, request, flash, render_template, session
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only

from task_manager.statuses.models import Status
from task_manager.tags.models import Tag
from task_manager.tasks.forms import CreateTask, EditTaskForm
from task_manager.tasks.models import Task, Plan, IntermediateTaskTag

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

    if not request.form:
        session['steps'] = []
    steps = session.get('steps', [])
    form = CreateTask(qnty_steps=len(steps), **choices)
    if form.add_step.data:
        if msg := get_error_for_step_add(form):
            flash(msg, "warning")
        else:
            step_id = int(form.step_name.data)
            status = Status.query.filter_by(id=step_id).one()
            step_name = status.name
            step = {'id': len(steps),
                    'step_id': step_id,
                    'step_name': step_name,
                    'start': form.start_step_date.data.toordinal(),
                    'end': form.planned_step_end.data.toordinal()}
            session['steps'] = steps + [step]
            form.step_name.data = None
            form.start_step_date.data = form.start_step_date.raw_data = None
            form.planned_step_end.data = form.planned_step_end.raw_data = None
    if form.del_step.data:
        if msg := get_error_for_step_delete(form):
            flash(msg, "warning")
        else:
            new_steps = []
            for step in steps:
                if str(step['id']) not in form.del_option.raw_data:
                    new_steps.append(step)
            form.del_option.raw_data = []
            session['steps'] = new_steps
    if form.submit.data:
        if msg := get_error_create_form(form, steps):
            flash(msg, "warning")
        elif create_task(form, normalize_steps_set(session['steps'])):
            flash('Task successfully created', 'success')
            return redirect(url_for('tasks.show_tasks_list'))
        else:
            flash('Error adding to database', 'danger')
    context = dict()
    context['form'] = form
    context['title'] = 'Create task'
    context['steps'] = normalize_steps_set(session['steps'])

    return render_template('tasks/task_creation.html', **context)


def create_task(form, steps):
    manager_id = current_user.id
    executor_id = form.executor.data
    task_name = form.task_name.data
    task_description = form.description.data
    task_start = sorted(list(map(lambda x: x['start'], steps)))[0]
    task_planned_end = sorted(list(map(lambda x: x['end'], steps)))[0]
    task = Task(name=task_name, description=task_description,
                manager_id=manager_id, executor_id=executor_id,
                start_date=task_start, planned_end_date=task_planned_end)
    try:
        db.session.add(task)
        db.session.flush()
        id = task.id
        for step in steps:
            plan_item = Plan(start_date=step['start'],
                             planned_end=step['end'],
                             status_id=step['step_id'],
                             task_id=id,
                             executor_id=executor_id)
            db.session.add(plan_item)
        for tag in form.tags.data:
            interlink = IntermediateTaskTag(
                task_id=id,
                tag_id=tag
            )
            db.session.add(interlink)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False
    return True


def extract_choices():
    choices = dict()
    executors = User.query.filter(User.role_id.in_([1, 2])).all()
    choices['executors'] = [(None, '   <------>     ')] + \
                           list(map(lambda x: (x.id, f"{x.first_name} {x.last_name}"), executors))
    tags = Tag.query.all()
    choices['tags'] = [(None, '   <------>     ')] + list(map(lambda x: (x.id, x.name), tags))
    statuses = Status.query.all()
    choices['step_names'] = [(None, '   <------>     ')] + list(map(lambda x: (x.id, x.name), statuses))
    return choices


def get_error_create_form(form, steps):
    if not steps:
        return "Provide a plan for task"
    if form.executor.data == 'None':
        return "Nominate an executor"
    if len(form.task_name.data) < 4:
        return "Name of task should be at least 4 characters"
    if len(list(Task.query.filter_by(name=form.task_name.data).all())) > 0:
        return "Task with such name exists in database"
    return False


def get_error_for_step_add(form):
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


def normalize_steps_set(steps):
    normalized = []

    for step in steps:
        normalized += [{'id': int(step['id']),
                        'step_id': int(step['step_id']),
                        'step_name': step['step_name'],
                        'start': date.fromordinal(step['start']),
                        'end': date.fromordinal(step['end'])}]
    key = lambda x: x['start']
    normalized.sort(key=key)
    return normalized


def get_error_for_step_delete(form):
    choices = form.del_option.raw_data
    if not choices:
        return "Select steps to delete"
    return False
