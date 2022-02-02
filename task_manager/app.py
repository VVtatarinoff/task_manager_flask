from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from task_manager.auths.users import users_bp


app = Flask(__name__)
app.register_blueprint(users_bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def index():
    return 'Hello'


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
