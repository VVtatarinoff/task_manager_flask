import logging

from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

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


@tasks_bp.route('/task_create')
@login_required
@permission_required(Permission.MANAGE)
def create_task():
    return redirect(url_for('main.index'))
