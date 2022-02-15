import logging

from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import abort

from task_manager.tags.forms import CreateTag, EditTagForm
from task_manager.tags.models import Tag

tags_bp = Blueprint('tags', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402
from task_manager.auths.users import permission_required  # noqa 402

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
    tag = Tag.query.filter_by(id=id).first()
    if tag is None:
        abort(404)
    context = dict()
    context['title'] = 'Tag detail'
    context['tag'] = tag

    return render_template('tags/tag_detail.html', **context)


@tags_bp.route('/tag_edit/<int:id>', methods=('POST', 'GET'))
@permission_required(Permission.MANAGE)
@login_required
def edit_tag(id):
    tag = Tag.query.filter_by(id=id).first()
    if tag is None:
        abort(404)
    form = EditTagForm(tag)
    context = dict()
    context['title'] = f'Edit tag #{tag.name}'
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.description = form.description.data
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            flash(f'{tag.name} could not be updated', 'error')
        else:
            flash(f'Details of tag #{tag.name} have been updated.')
        return redirect(url_for('tags.show_tag_detail', id=tag.id))
    context['form'] = form
    context['tag'] = tag
    return render_template('tags/edit_tag.html', **context)
