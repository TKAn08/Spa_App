from flask import render_template, app, Blueprint

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')