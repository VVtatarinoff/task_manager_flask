from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asdaggfe55fgsdf'

db = SQLAlchemy(app)
# db.init_app(app)

from task_manager.auths.users import users_bp
from task_manager.main import main_bp

app.register_blueprint(users_bp)
app.register_blueprint(main_bp)
bootstrap = Bootstrap(app)
