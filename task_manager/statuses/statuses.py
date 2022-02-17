import logging

from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from task_manager.statuses.forms import CreateStatus, EditStatusForm
from task_manager.statuses.models import Status

status_bp = Blueprint('statuses', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402
from task_manager.auths.users import permission_required  # noqa 402

logger = logging.getLogger(__name__)


@status_bp.route('/statuses')
@login_required
def show_statuses_list():
    logger.disabled = False
    logger.debug(f'Status list request {request.method}, ars {request.args}')
    logger.debug(f'Status list request, tags = {list(Status.query.all())}')
    context = dict()
    context['title'] = 'Statuses'
    context['table_heads'] = ('ID', 'Name',
                              'Creation date')
    statuses = []
    try:
        statuses = Status.query.all()
    except SQLAlchemyError:
        flash('Database error ', 'danger')
    context['table_data'] = statuses
    return render_template('statuses/status_list.html', **context)


@status_bp.route('/create_status', methods=('POST', 'GET'))
@login_required
@permission_required(Permission.MANAGE)
def create_status():
    logger.disabled = False
    logger.debug(f'status creation request {request.method}')
    form = CreateStatus()
    if form.validate_on_submit():
        logger.debug(f'status creation form validated {request.form["name"]}')
        try:
            status = Status(name=request.form['name'],
                            description=request.form['description'],
                            )
            db.session.add(status)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error during adding to DataBase', 'danger')
        else:
            logger.debug(f'status created {request.form["name"]}')
            flash(f'Status {request.form["name"]} created', 'success')
        return redirect(url_for('statuses.show_statuses_list'))
    context = dict()
    context['form'] = form
    context['title'] = 'Create status'
    return render_template('statuses/status_creation.html', **context)


@status_bp.route('/status_detail/<int:id>')
@login_required
def show_status_detail(id):
    status = Status.query.filter_by(id=id).first_or_404()
    context = dict()
    context['title'] = 'Status detail'
    context['status'] = status

    return render_template('statuses/status_detail.html', **context)


@status_bp.route('/status_edit/<int:id>', methods=('POST', 'GET'))
@login_required
@permission_required(Permission.MANAGE)
def edit_status(id):
    status = Status.query.filter_by(id=id).first_or_404()
    logger.disabled = False
    logger.debug(f'Status update {request.method}, status {status.name}')
    form = EditStatusForm(status)
    context = dict()
    context['title'] = f'Edit status {status.name}'
    if form.validate_on_submit():
        status.name = form.name.data
        status.description = form.description.data
        logger.debug(
            f'Status update form validated {status.name}, {status.description}')
        try:
            db.session.add(status)
            db.session.commit()
        except SQLAlchemyError:
            flash(f'Status {status.name} could not be updated', 'danger')
        else:
            flash(f'Details of status "{status.name}" have been updated.',
                  "success")
        return redirect(url_for('statuses.show_status_detail', id=status.id))
    context['form'] = form
    context['status'] = status
    return render_template('statuses/edit_status.html', **context)
