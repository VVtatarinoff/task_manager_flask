import logging

from flask import Blueprint, redirect, url_for
from flask_login import login_required


status_bp = Blueprint('statuses', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402

logger = logging.getLogger(__name__)


@status_bp.route('/statuses')
@login_required
def show_statuses_list():
    return redirect(url_for('main.index'))
