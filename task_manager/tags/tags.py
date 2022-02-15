import logging

from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from task_manager.tags.forms import CreateTag
from task_manager.tags.models import Tag

tags_bp = Blueprint('tags', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402
from task_manager.auths.users import permission_required
logger = logging.getLogger(__name__)


@tags_bp.route('/tags')
@login_required
def show_tags_list():
    logger.disabled = False
    logger.debug(f'Tag list request {request.method}, ars {request.args}')
    logger.debug(f'Tag list request, tags = {list(Tag.query.all())}')
    context = dict()
    context['title'] = 'Tags'
    context['table_heads'] = ('ID', 'Name',
                              'Creation date')
    tags = []
    try:
        tags = Tag.query.all()
    except SQLAlchemyError as e:
        flash('Database error ', e)
    context['table_data'] = tags
    return render_template('tags/tag_list.html', **context)


@tags_bp.route('/create_tag', methods=('POST', 'GET'))
@permission_required(Permission.MANAGE)
@login_required
def create_tag():
    logger.disabled = False
    logger.debug(f'tag creation request {request.method}')
    form = CreateTag()
    if form.validate_on_submit():
        logger.debug(f'tag creation form validated {request.form["name"]}')
        try:
            tag = Tag(name=request.form['name'],
                      description=request.form['description'],
                        )
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error during adding to DataBase', 'error')
        else:
            logger.debug(f'tag created {request.form["name"]}')
            flash(f'Tag {request.form["name"]} created', 'success')
        return redirect(url_for('tags.show_tags_list'))
    context = dict()
    context['form'] = form
    context['title'] = 'Create tag'
    return render_template('tags/tag_creation.html', **context)


@tags_bp.route('/tag_detail/<int:id>')
@login_required
def show_tag_detail(id):
    return redirect(url_for('main.index'))
