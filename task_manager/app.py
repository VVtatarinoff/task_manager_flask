from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from task_manager.auths.users import users_bp


app = Flask(__name__)
app.register_blueprint(users_bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asdaggfe55fgsdf'
bootstrap = Bootstrap(app)

@app.route('/')
def index():

    return render_template('base.html')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
