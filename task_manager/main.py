from flask import render_template
from flask import Blueprint
from task_manager import app

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def index():
    return render_template('index.html')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
