import logging

from flask import Blueprint, redirect, url_for
from flask_login import login_required

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402

logger = logging.getLogger(__name__)


@tasks_bp.route('/tasks')
@login_required
def show_tasks_list():
    return redirect(url_for('main.index'))
