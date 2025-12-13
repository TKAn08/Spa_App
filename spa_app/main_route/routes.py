from flask import render_template, Blueprint, request, redirect, session
from flask_login import login_required, current_user, login_manager
import math
from spa_app.dao.user_dao import get_age_user, change_password
from spa_app.dao import services_dao, user_dao, employee_dao


main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    outstanding_services = services_dao.get_outstanding_services()
    return render_template('index.html', outstanding_services=outstanding_services)

@main_bp.route('/service', methods=['GET', 'POST'])
def services_view():
    page = request.args.get('page', 1, type=int)
    cate_id = request.args.get('cate_id', 1, type=int)
    search = request.args.get('search', None, type=str)
    services = services_dao.load_services(page=page, cate_id=cate_id, search=search)
    categories = services_dao.load_categories()
    pages = math.ceil(services_dao.count_services(cate_id) / services_dao.count_services_per_page())
    return render_template('services/services.html', services = services,
                           pages = pages, current_page = page, categories = categories)


@main_bp.route('/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    # Lấy tab từ query string, ví dụ ?tab=information hoặc ?tab=change-password
    tab = request.args.get('tab')  # mặc định là thông tin cá nhân
    age = get_age_user(current_user.DOB)
    message = None

    if tab == 'change_password' and request.method == 'POST':
        old_password = request.form.get('old-password') or None
        new_password = request.form.get('new-password') or None
        confirm = request.form.get('confirm_new-password') or None
        if not current_user.check_password(old_password):
            message = "Mật khẩu hiện tại không đúng !"
            # session['modal-type'] = 'error'
        elif new_password != confirm:
            message = "Mật khẩu không khớp !"
            # session['modal-type'] = 'error'
        else:
            message = "Thay đổi mật khẩu thành công !"
            user_dao.change_password(current_user, new_password)
            # session['modal-type'] = 'success'
        session['modal-message'] = message

    if tab == 'information' and request.method == 'POST':
        name = request.form.get('name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        address = request.form.get('address')
        phone_number = request.form.get('phone-number')

        if (user_dao.check_invalid_phone_number(phone_number)):
            message = "Thay đổi tin thất bại, số điện thoại đã được đăng ký !"
            # session['modal-type'] = 'error'

        else:
            message = "Thay đổi thông tin thành công !"
            user_dao.change_information(current_user, name, gender, dob, address, phone_number)
            # session['modal-type'] = 'success'
        session['modal-message'] = message

    if tab == 'change_password':
        template = 'information-user/change-password.html'
    else:
        template = 'information-user/information.html'

    return render_template(template, username=username, tab=tab, age=age, message=message)


@main_bp.route('/service/<int:id>', methods=['GET', 'POST'])
def services_detail_view(id):
    return render_template('services/service-detail.html',
                           service=services_dao.get_service_by_id(id))

@main_bp.route('/contact')
def contact_view():
    return render_template('contact.html' )

@main_bp.route('/staff')
def staff_view():
    employees = employee_dao.load_all_employee()
    return render_template('staff.html',employees = employees)