import logging

from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.orm import load_only
from werkzeug.exceptions import abort

users_bp = Blueprint('users', __name__, template_folder='templates')

from task_manager import db  # noqa 402
from task_manager.auths.models import User, Permission, Role  # noqa 402
from task_manager.auths.forms import (CreateUser, SignInForm,  # noqa 402
                                      EditProfileForm, EditProfileFormAdmin)  # noqa 402

FILTERS = ['Administrator', 'Executor', 'Manager']
logger = logging.getLogger(__name__)


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def self_or_admin_required(msg):
    def decorator(f):
        @wraps(f)
        def decorated_function(username):
            if (current_user.name != username) and (
                    not current_user.is_administrator()):
                flash(msg)
                return redirect(url_for('main.index'))
            return f(username)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


@users_bp.context_processor
def inject_permissions():
    return dict(Permission=Permission)


@users_bp.route('/register', methods=('POST', 'GET'))
def register():
    logger.disabled = False
    logger.debug(f'user registration request {request.method}')
    form = CreateUser()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        logger.debug(f'registration form validated {request.form["email"]}')
        try:
            user = User(email=request.form['email'],
                        name=request.form['name'],
                        first_name=request.form['first_name'],
                        last_name=request.form['last_name'],
                        password=request.form['psw1'],
                        )
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error during adding to DataBase', 'error')
        else:
            logger.debug(f'user registered {request.form["email"]}')
            flash('User registered', 'success')
        return redirect(url_for('users.login'))
    context = dict()
    context['form'] = form
    context['title'] = 'Registration'
    return render_template('users/user_register.html', **context)


@users_bp.route('/login', methods=('POST', 'GET'))
def login():  # noqa 901
    logger.disabled = False
    logger.debug(f'login request {request.method}')
    form = SignInForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    context = dict()
    context['form'] = form
    context['title'] = 'Authorization'
    if form.validate_on_submit():
        logger.debug(f'validated login form: email'
                     f' {request.form["email"]} psw {request.form["psw"]}')
        try:
            user = User.query.filter_by(email=request.form['email']).one()
        except SQLAlchemyError:
            flash('Invalid email or password.', 'error')
            logger.debug(f'login no such data in db:'
                         f' email {request.form["email"]} '
                         f'psw {request.form["psw"]}')
            return render_template('users/user_login.html', **context)

        if user and user.verify_password(request.form['psw']):
            login_user(user, form.remember_me.data)
            flash(f'{user.name} logged in', 'success')
            user.last_seen = datetime.utcnow()
            try:
                db.session.commit()
            except SQLAlchemyError:
                flash(f'{user.name} could not update bd', 'error')
            previous_page = request.args.get('next')
            if previous_page and previous_page != url_for('users.log_out'):
                return redirect(previous_page)
            return redirect(url_for('main.index'))
        flash('Invalid email or password.')
    return render_template('users/user_login.html', **context)


@users_bp.route('/logout')
@login_required
def log_out():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@users_bp.route('/users')
def get_user_list():
    logger.disabled = False
    logger.debug(f'User list request {request.method}, ars {request.args}')
    logger.debug(f'User list request, users = {list(User.query.all())}')
    request_filter = dict([(x, x in request.args) for x in FILTERS])
    context = dict()
    context.update(request_filter)
    context['title'] = 'Users'
    context['table_heads'] = ('ID', 'User name',
                              'Full name', 'Creation date', 'Role')
    checked_options = list(filter(lambda item: item[1], request_filter.items()))
    checked_options = list(map(lambda x: x[0], checked_options))
    logger.debug(f'User list request, checked_id = {checked_options}')
    checked_id = Role.query.filter(
        Role.name.in_(checked_options)).options(load_only('id')).all()
    checked_id = list(map(lambda x: x.id, checked_id))
    logger.debug(f'User list request, checked_id = {checked_id}')
    users = []

    try:
        users = User.query.filter(User.role_id.in_(checked_id)).all()
    except SQLAlchemyError as e:
        flash('Database error ', e)
    context['table_data'] = users
    return render_template('users/user_list.html', **context)


@users_bp.route('/profile/<string:username>')
@login_required
def show_profile(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        abort(404)
    context = dict()
    context['title'] = 'User profile'
    context['user'] = user
    return render_template('users/user_profile.html', **context)


@users_bp.route('/delete/<int:id>')
@login_required
def delete_user(id):
    pass


@users_bp.route('/update/<string:username>', methods=['GET', 'POST'])
@login_required
@self_or_admin_required("You could not edit other user's profile")
def edit_profile(username):
    user = User.query.filter_by(name=username).first()
    logger.disabled = False
    logger.debug(f'User profile update {request.method}, users {user.name}')
    is_admin = current_user.is_administrator()
    if user is None:
        abort(404)
    form = EditProfileFormAdmin(user) if is_admin else EditProfileForm(user)
    context = dict()
    context['title'] = f'Edit profile of {user.name}'
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.location = form.location.data
        if is_admin:
            user.email = form.email.data
            user.role_id = form.role.data
            logger.debug(f'User admin update email {user.email}, role {user.role_id}')
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            flash(f'{user.name} could not be updated', 'error')
        else:
            flash(f'Profile of {user.name} has been updated.')
        return redirect(url_for('users.show_profile', username=user.name))
    context['form'] = form
    context['user'] = user
    return render_template('users/edit_profile.html', **context)
