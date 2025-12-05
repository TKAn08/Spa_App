from flask import render_template, app, Blueprint
from spa_app.dao import services_dao


main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    services = services_dao.load_services_for_main_page()
    return render_template('index.html',services = services)