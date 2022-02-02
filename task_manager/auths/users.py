from flask import Blueprint
users_bp = Blueprint('users', __name__)

from task_manager.models import Users
