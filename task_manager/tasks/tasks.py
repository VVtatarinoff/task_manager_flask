import logging
from datetime import date

from flask import (Blueprint, redirect, url_for, request,
                   flash, render_template, session)
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from task_manager import db
from task_manager.statuses.models import Status
from task_manager.tasks.forms import CreateTask, EditTaskForm
from task_manager.tasks.models import Task
from task_manager.auths.models import Permission
from task_manager.auths.users import permission_required
from task_manager.tasks.session import SessionPlan

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')
from task_manager.tasks.utils import (create_tasks_list,
                                      upload_task,
                                      get_error_modifing_task)

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
    except SQLAlchemyError:
        flash('Database error ', 'danger')
        return redirect(url_for('main.index'))
    context['table_data'] = create_tasks_list(tasks)
    return render_template('tasks/task_list.html', **context)


@tasks_bp.route('/task_detail/<int:id>')
@login_required
def show_task_detail(id):
    try:
        task = Task.query.filter_by(id=id).one()
    except NoResultFound:
        flash('No such task in the database', "warning")
        return redirect(url_for('main.index'))
    context = dict()
    context['task'] = task
    context['title'] = 'Task page'
    return render_template('tasks/task_profile.html', **context)


@tasks_bp.route('/task_update/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def update_task(id):
    task = Task.query.filter_by(id=id).one()
    if msg := get_error_modifing_task(task):
        flash(msg, 'warning')
        return redirect(url_for("tasks.show_task_detail", id=id))
    if not request.form:
        session['tags'] = []
        steps = []
        for step in task.plan:
            step_dict = dict()
            step_dict['id'] = step.id
            step_dict['step_id'] = step.status.id
            step_dict['step_name'] = step.status.name
            step_dict['start'] = step.start_date.toordinal()
            step_dict['end'] = step.planned_end.toordinal()
            steps += [step_dict]
        session['steps'] = steps
    form = EditTaskForm(task)
    context = dict()
    context['form'] = form
    context['title'] = 'Change task'
    context['steps'] = normalize_steps_set(session['steps'])

    return render_template('tasks/task_update.html', **context)


@tasks_bp.route('/task_delete/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def delete_task(id):
    task = Task.query.filter_by(id=id).one()
    if msg := get_error_modifing_task(task):
        flash(msg, "danger")
        return redirect(url_for("tasks.show_task_detail", id=id))
    try:
        for step in task.plan:
            db.session.delete(step)
            db.session.flush()
        db.session.delete(task)
        db.session.commit()
    except SQLAlchemyError:
        flash('Database error during delete transaction', 'danger')
    else:
        flash('The task was successfully deleted', 'success')
    return redirect(url_for("tasks.show_tasks_list"))


def convert_date_to_string(raw_date: date) -> str:
    return raw_date.strftime('%d-%m-%Y')


def convert_string_to_date(date_string: str) -> date:
    day, month, year = tuple(map(int, date_string.split('-')))
    return date(year, month, day)


@tasks_bp.route('/task_create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def create_task():  # noqa 901
    steps=SessionPlan(new=not request.form)
    form = CreateTask()
    if form.add_step.data and form.check_adding_step_form():
        step_id = int(form.status_name.data)
        steps.add_step_from_form(status_id=step_id, form=form)
        form.clear_step_data()
    if form.del_step.data and form.del_option.raw_data:
        steps.remove_step_from_session(form.del_option.raw_data)
        form.del_option.raw_data = []
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
    return render_template('tasks/task_creation.html', **context)


def normalize_steps_set(steps):
    normalized = []

    for step in steps:
        normalized += [{'id': int(step['id']),
                        'step_id': int(step['step_id']),
                        'step_name': step['step_name'],
                        'start': convert_string_to_date(step['start']),
                        'end': convert_string_to_date(step['end'])}]
    normalized.sort(key=lambda x: x['start'])
    return normalized
