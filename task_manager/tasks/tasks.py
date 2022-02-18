import logging
from datetime import date

from flask import (Blueprint, redirect, url_for, request,
                   flash, render_template, session)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from task_manager.statuses.models import Status
from task_manager.tasks.forms import CreateTask
from task_manager.tasks.models import Task, Plan, IntermediateTaskTag
from task_manager.tasks.utils import create_tasks_list
from task_manager.auths.models import Permission
from task_manager.auths.users import permission_required
from task_manager import db

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


@tasks_bp.route('/tasks')
@login_required
def show_tasks_list():
    logger.disabled = False
    logger.debug(f'Task list request {request.method}, ars {request.args}')
    logger.debug(f'Task list request, tasks = {list(Task.query.all())}')
    context = dict()
    context['title'] = 'Tasks'
    context['table_heads'] = ('Name', 'Executor', 'Manager', 'Planned start',
                              'Actual start', 'Planned end', 'Actual end',
                              'Current status')
    try:
        tasks = Task.query.all()
    except SQLAlchemyError as e:
        flash('Database error ', e)
        return redirect(url_for('main.index'))
    context['table_data'] = create_tasks_list(tasks)
    return render_template('tasks/task_list.html', **context)


@tasks_bp.route('/task_detail/<int:id>')
@login_required
def show_task_detail(id):
    return redirect(url_for('main.index'))


@tasks_bp.route('/task_create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def create_task():  # noqa 901
    if not request.form:
        session['steps'] = []
    steps = session.get('steps', [])
    form = CreateTask()
    if form.add_step.data and form.check_adding_step_form():
        step_id = int(form.step_name.data)
        status = Status.query.filter_by(id=step_id).one()
        step_name = status.name
        step = {'id': len(steps),
                'step_id': step_id,
                'step_name': step_name,
                'start': form.start_step_date.data.toordinal(),
                'end': form.planned_step_end.data.toordinal()}
        steps += [step]
        session['steps'] = steps
        form.clear_step_data()
    if form.del_step.data and form.del_option.raw_data:
        new_steps = []
        counter = 0
        for step in steps:
            if str(step['id']) not in form.del_option.raw_data:
                step['id'] = counter
                counter += 1
                new_steps.append(step)
        form.del_option.raw_data = []
        session['steps'] = new_steps
    if form.submit.data and form.check_create_task_form(new=True):
        if not steps:
            flash("Provide a plan for task", 'danger')
        elif upload_task(form, normalize_steps_set(session['steps'])):
            flash('Task successfully created', 'success')
            return redirect(url_for('tasks.show_tasks_list'))
        else:
            flash('Error adding to database', 'danger')
    context = dict()
    context['form'] = form
    context['title'] = 'Create task'
    context['steps'] = normalize_steps_set(session['steps'])

    return render_template('tasks/task_creation.html', **context)


def upload_task(form, steps):
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
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def get_error_create_form(form, steps):
    if not steps:
        return "Provide a plan for task"
    return False


def normalize_steps_set(steps):
    normalized = []

    for step in steps:
        normalized += [{'id': int(step['id']),
                        'step_id': int(step['step_id']),
                        'step_name': step['step_name'],
                        'start': date.fromordinal(step['start']),
                        'end': date.fromordinal(step['end'])}]
    normalized.sort(key=lambda x: x['start'])
    return normalized
