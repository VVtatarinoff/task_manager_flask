import logging

import dateutil.utils
from flask import (Blueprint, redirect, url_for, request,
                   flash, render_template)
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from task_manager import db
from task_manager.tasks.forms import CreateTask, UpdateTask
from task_manager.tasks.models import Task, Plan
from task_manager.auths.models import Permission
from task_manager.auths.users import permission_required
from task_manager.tasks.utils import (create_tasks_list,
                                      upload_task,
                                      get_error_modifing_task, change_task)

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')

logger = logging.getLogger(__name__)

TITLES = {'list': 'Tasks',
          'detail': 'Task page',
          'update': 'Change task',
          'delete': 'Delete task',
          'create': 'Create task'
          }


@tasks_bp.route('/tasks')
@login_required
def show_tasks_list():
    logger.disabled = False
    logger.debug(f'Task list request {request.method}, ars {request.args}')
    logger.debug(f'Task list request, tasks = {list(Task.query.all())}')
    context = dict()
    context['title'] = TITLES['list']
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
    context['title'] = TITLES['detail']
    return render_template('tasks/task_profile.html', **context)


@tasks_bp.route('/task_update/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def update_task(id):  # noqa 901
    task = Task.query.filter_by(id=id).one()
    if msg := get_error_modifing_task(task):
        flash(msg, 'warning')
        return redirect(url_for("tasks.show_task_detail", id=id))
    if request.method == "GET":
        form = UpdateTask(task=task)
    else:
        form = UpdateTask()
    if form.add_step_button.data:
        form.add_step(0, new=True)
    if form.del_step_button.data and form.del_option.raw_data:
        form.delete_step()
    if form.submit.data and form.check_create_task_form():
        task_check_ids = list(
            map(lambda x: x.id,
                Task.query.filter_by(name=form.task_name.data).all()))
        task_dublicate_name = list(
            filter(lambda x: x != task.id, task_check_ids))
        if task_dublicate_name:
            form.task_name.errors = [
                "Task with such name exists in database"]
        elif change_task(task, form):
            flash('Task successfully updated', 'success')
            return redirect(url_for('tasks.show_tasks_list'))
        else:
            flash('Error adding to database', 'danger')
    context = dict()
    context['form'] = form
    context['title'] = TITLES['update']
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
    context = dict()
    context['title'] = TITLES['delete']
    return redirect(url_for("tasks.show_tasks_list"))


@tasks_bp.route('/task_create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE)
def create_task():
    form = CreateTask()
    if form.add_step_button.data:
        form.add_step(0, new=True)
    if form.del_step_button.data and form.del_option.raw_data:
        form.delete_step()
    if form.submit.data and form.check_create_task_form():
        if list(Task.query.filter_by(name=form.task_name.data).all()):
            form.task_name.errors = [
                "Task with such name exists in database"]
        elif upload_task(form):
            flash('Task successfully created', 'success')
            return redirect(url_for('tasks.show_tasks_list'))
        else:
            flash('Error adding to database', 'danger')

    context = dict()
    context['form'] = form
    context['title'] = TITLES['create']
    return render_template('tasks/task_creation.html', **context)


@tasks_bp.route('/task_step_start/<int:id>', methods=['GET'])
@login_required
def start_step(id):
    try:
        step = Plan.query.filter_by(id=id).one()
    except SQLAlchemyError:
        flash('No such step exists in database', 'warning')
        return redirect(url_for('main.index'))
    try:
        step.actual_start = dateutil.utils.today()
        db.session.add(step)
        db.session.commit()
        flash('Step started', 'success')
    except SQLAlchemyError:
        flash('Error changing the database', 'error')
        db.session.rollback()
    return redirect(url_for('tasks.show_task_detail', id=step.task_id))


@tasks_bp.route('/task_step_end/<int:id>', methods=['GET'])
@login_required
def end_step(id):
    try:
        step = Plan.query.filter_by(id=id).one()
    except SQLAlchemyError:
        flash('No such step exists in database', 'warning')
        return redirect(url_for('main.index'))
    try:
        step.actual_end_date = dateutil.utils.today()
        db.session.add(step)
        db.session.commit()
        flash('Step ended', 'success')
    except SQLAlchemyError:
        flash('Error changing the database', 'error')
        db.session.rollback()
    return redirect(url_for('tasks.show_task_detail', id=step.task_id))
