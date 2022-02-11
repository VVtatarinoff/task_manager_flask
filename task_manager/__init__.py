from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment

from config import config


login_manager = LoginManager()
moment = Moment()
db = SQLAlchemy()
bootstrap = Bootstrap()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from task_manager.auths.models import AnonymousUser  # noqa 402
    from task_manager.auths.users import users_bp  # noqa 402
    from task_manager.main import main_bp  # noqa 402

    login_manager.anonymous_user = AnonymousUser

    app.register_blueprint(users_bp)
    app.register_blueprint(main_bp)

    return app
