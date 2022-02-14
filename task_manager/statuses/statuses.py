import logging

from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy.orm import load_only

status_bp = Blueprint('statuses', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402

logger = logging.getLogger(__name__)


@status_bp.route('/statuses')
@login_required
def show_statuses_list():
    return redirect(url_for('main.index'))