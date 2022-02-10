from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user

users_bp = Blueprint('users', __name__, template_folder='templates')

from task_manager import db
from task_manager.auths.models import User
from task_manager.auths.forms import CreateUser, SignInForm


@users_bp.route('/register', methods=('POST', 'GET'))
def register():
    form = CreateUser()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        try:
            user = User(email=request.form['email'],
                        name=request.form['name'],
                        first_name=request.form['first_name'],
                        last_name=request.form['last_name'],
                        password=request.form['psw1']
                        )
            # u.password = request.form['psw1']
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Error during adding to DataBase', 'error')
        else:
            flash('User registered', 'success')
        return redirect(url_for('users.sign_in'))
    context = dict()
    context['form'] = form
    context['title'] = 'Registration'
    return render_template('users/user_register.html', **context)


@users_bp.route('/login', methods=('POST', 'GET'))
def sign_in():
    form = SignInForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    context = dict()
    context['form'] = form
    context['title'] = 'Authorization'
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=request.form['email']).one()
        except:
            flash('No such e-mail in database', 'error')
            render_template('users/user_login.html', **context)
        else:
            if user and user.verify_password(request.form['psw']):
                login_user(user, form.remember_me.data)
                flash(f'{user.name} logged in', 'success')
                previous_page = request.args.get('next')
                if previous_page and previous_page != url_for('users.log_out'):
                    return redirect(previous_page)
                return redirect(url_for('main.index'))
            flash('Invalid username or password.')
    return render_template('users/user_login.html', **context)


@users_bp.route('/logout')
@login_required
def log_out():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@users_bp.route('/users')
def get_user_list():
    context = dict()
    context['title'] = 'Users'
    context['table_heads'] = ('ID', 'User name',
                              'Full name', 'Creation date')
    users = []
    try:
        users = User.query.all()
    except Exception as e:
        flash(e)
    context['table_data'] = users
    return render_template('users/user_list.html', **context)


@users_bp.route('/delete/<int:id>')
@login_required
def delete_user(id):
    pass
