from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment

app = Flask(__name__)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'users.login'
moment = Moment(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asdaggfe55fgsdf'
app.config['TASK_MANAGER_ADMIN'] = 'vova@mail.ru'

db = SQLAlchemy(app)
# db.init_app(app)

from task_manager.auths.models import AnonymousUser # noqa 402
from task_manager.auths.users import users_bp   # noqa 402
from task_manager.main import main_bp   # noqa 402

login_manager.anonymous_user = AnonymousUser
login_manager.init_app(app)
app.register_blueprint(users_bp)
app.register_blueprint(main_bp)
bootstrap = Bootstrap(app)
