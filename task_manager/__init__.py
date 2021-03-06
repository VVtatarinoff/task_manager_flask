import logging
import sys
from pathlib import Path

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment

from task_manager.config import config


BASE_DIR = Path(__file__).resolve().parent.parent
login_manager = LoginManager()
moment = Moment()
db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()


def init_logger(config_name):
    logger = logging.getLogger('task_manager')
    logger.setLevel(logging.DEBUG)
    if config[config_name].LOG_TO_STDOUT:
        sm = logging.StreamHandler(stream=sys.stdout)
    else:
        sm = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter('%(asctime)s :: %(name)s :'
                                  ': %(levelname)s :: %(message)s')
    sm.setFormatter(formatter)
    sm.setLevel('DEBUG')
    logger.addHandler(sm)
    logger_file = BASE_DIR / "logs/task_manager.log"
    if logger_file.is_file():
        fn = logging.FileHandler(BASE_DIR / "logs/task_manager.log", mode='w')
        fn.setFormatter(formatter)
        fn.setLevel('DEBUG')
        logger.addHandler(fn)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from task_manager.auths.models import AnonymousUser  # noqa 402
    from task_manager.auths.users import users_bp  # noqa 402
    from task_manager.main import main_bp  # noqa 402
    from task_manager.statuses.statuses import status_bp # noqa 402
    from task_manager.tags.tags import tags_bp  # noqa 402
    from task_manager.tasks.tasks import tasks_bp # noqa 402

    login_manager.anonymous_user = AnonymousUser

    app.register_blueprint(users_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(tasks_bp)
    init_logger(config_name)
    return app


if __name__ == '__main__':
    print('hello')
