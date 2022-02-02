from flask import Blueprint

users_bp = Blueprint('users', __name__)

from task_manager.models import Users


@users_bp.route('/register', methods=('POST', 'GET'))
def register():
    return 'register'


@users_bp.route('/signin', methods=('POST', 'GET'))
def sign_in():
    return 'signing in'
