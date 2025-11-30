from datetime import datetime
from spa_app.models import User
from flask import render_template, request, redirect, flash, Blueprint
from flask_login import current_user, login_user, logout_user
from spa_app.dao import services_dao


services_bp = Blueprint('services_bp', __name__)

@services_bp.route('/services', methods=['GET', 'POST'])
def services_view():
    services = services_dao.load_services()
    return render_template('services/services.html', services = services)
