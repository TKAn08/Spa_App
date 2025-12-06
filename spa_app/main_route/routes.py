from flask import render_template, Blueprint, request, redirect
from flask_login import login_required, current_user, login_manager

from spa_app.dao import services_dao


main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    services = services_dao.load_services_for_main_page()
    return render_template('index.html',services = services)

@main_bp.route('/service', methods=['GET', 'POST'])
def services_view():
    services = services_dao.load_services()
    return render_template('services/services.html', services = services)


@main_bp.route('/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    # Lấy tab từ query string, ví dụ ?tab=information hoặc ?tab=change-password
    tab = request.args.get('tab')  # mặc định là thông tin cá nhân

    if tab == 'change_password':
        template = 'information-user/change-password.html'
    else:
        template = 'information-user/information.html'

    return render_template(template, username=username, tab=tab)

