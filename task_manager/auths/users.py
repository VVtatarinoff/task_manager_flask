from flask import Blueprint, render_template, request, redirect, url_for, session, flash

users_bp = Blueprint('users', __name__, template_folder='templates')

from task_manager import db
from task_manager.models import Users
from task_manager.auths.forms import CreateUser, SignInForm
from werkzeug.security import generate_password_hash, check_password_hash


@users_bp.route('/register', methods=('POST', 'GET'))
def register():
    form = CreateUser()
    if form.validate_on_submit():
        try:
            hash = generate_password_hash(request.form['psw1'])
            u = Users(email=request.form['email'],
                      name=request.form['name'],
                      first_name=request.form['first_name'],
                      last_name=request.form['last_name'],
                      password=hash
                      )
            db.session.add(u)
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
    context = dict()
    context['form'] = form
    context['title'] = 'Authorization'
    if form.validate_on_submit():
        try:
            u = Users.query.filter_by(email=request.form['email']).one()
        except:
            flash('No such e-mail in database', 'error')
            render_template('users/user_login.html', **context)
        else:
            if u and check_password_hash(u.password,request.form['psw']):
                session['logged'] == True
                flash('User logged in', 'success')
                print(session['logged'])
    return render_template('users/user_login.html', **context)


@users_bp.route('/users')
def get_user_list():
    context = dict()
    context['title'] = 'Users'
    context['table_heads'] = ('ID', 'User name',
                              'Full name', 'Creation date')
    users = []
    try:
        users = Users.query.all()
    except:
        print('Db access error')

    context['table_data'] = users
    return render_template('users/user_list.html', **context)
