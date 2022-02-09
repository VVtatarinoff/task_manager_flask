from flask import Flask, render_template, session
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

# from task_manager.auths.users import users_bp
#import task_manager.models
from task_manager import app


#app = Flask(__name__)
#app.register_blueprint(users_bp)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tm.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = 'asdaggfe55fgsdf'

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    return render_template('index.html')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
