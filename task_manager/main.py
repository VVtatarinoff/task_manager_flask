from flask import render_template
from flask import Blueprint

main_bp = Blueprint('main', __name__,
                    template_folder='templates',
                    static_folder='static')


@main_bp.route('/')
def index():
    return render_template('index.html')
