from flask import Blueprint, render_template

users_bp = Blueprint('users', __name__, template_folder='templates')

from task_manager.models import Users


@users_bp.route('/register', methods=('POST', 'GET'))
def register():
    return 'register'


@users_bp.route('/signin', methods=('POST', 'GET'))
def sign_in():
    return 'signing in'


@users_bp.route('/users')
def get_user_list():
    context = dict()
    context['Title'] = 'Users'
    context['table_heads'] = ('ID', 'User name',
                              'Full name', 'Creation date')
    users = []
    try:
        users = Users.query.all()
    except:
        print('Db access error')

    context['table_data'] = users
    return render_template('users/user_list.html', **context)
