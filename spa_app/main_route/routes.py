from datetime import datetime, date, timedelta
from flask import render_template, Blueprint, request, redirect, session, jsonify, url_for, flash
from flask_login import login_required, current_user
import math
from spa_app import db
from spa_app.dao.user_dao import get_age_user, change_password
from spa_app.dao import services_dao, user_dao, employee_dao
from spa_app.forms.booking_form import BookingConfirmForm, BookingStep4Form, BookingStep3Form, BookingStep2Form, \
    BookingStep1Form
from spa_app.helpers import cloudinary_helpers
from spa_app.models import Setting, Booking, User, BookingStatus, Service, Employee, Category  # THÊM Category
from spa_app.helpers.booking_helpers import is_booking_valid, auto_assign_employee
from spa_app.decorator import user_only_required

main_bp = Blueprint('main_bp', __name__)

#Trang chính
@main_bp.route('/')
@user_only_required
def index():
    outstanding_services = services_dao.get_outstanding_services()
    return render_template('index.html', outstanding_services=outstanding_services)

#Trang service
@main_bp.route('/service', methods=['GET', 'POST'])
@user_only_required
def services_view():
    page = request.args.get('page', 1, type=int)
    cate_id = request.args.get('cate_id', None, type=int)
    search = request.args.get('search', None, type=str)
    services = services_dao.load_services(page=page, cate_id=cate_id, search=search)
    categories = services_dao.load_categories()
    pages = math.ceil(services_dao.count_services(cate_id) / services_dao.count_services_per_page())
    return render_template('services/services.html', services=services,
                           pages=pages, current_page=page, categories=categories)

#Trang thông tin của 1 user
@main_bp.route('/<username>', methods=['GET', 'POST'])
@user_only_required
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
        avatar_file = request.files.get('avatar')
        if (user_dao.check_invalid_phone_number(phone_number)):
            message = "Thay đổi tin thất bại, số điện thoại đã được đăng ký !"


        else:
            #Gán vào biến avatar
            avatar = cloudinary_helpers.import_to_cloudinary(avatar_file)

            message = "Thay đổi thông tin thành công !"
            user_dao.change_information(current_user, name, gender, dob, address, phone_number, avatar)

        #Lưu message success hoặc error để xử lý
        session['modal-message'] = message

    if tab == 'change_password':
        template = 'information-user/change-password.html'
    else:
        template = 'information-user/information.html'
    # ===== BOOKINGS OF CURRENT USER =====
    bookings = Booking.query.filter_by(customer_id=current_user.id) \
        .order_by(Booking.date.desc(), Booking.time.desc()) \
        .all()

    return render_template(
        template,
        username=username,
        tab=tab,
        age=age,
        message=message,
        bookings=bookings
    )

#Trang thông tin của 1 dịch vụ
@main_bp.route('/service/<int:id>', methods=['GET', 'POST'])
@user_only_required
def services_detail_view(id):
    return render_template('services/service-detail.html',
                           service=services_dao.get_service_by_id(id))

    return render_template('services/service-detail.html', service=services_dao.get_service_by_id(id))

#Trang liên hệ
@main_bp.route('/contact')
@user_only_required
def contact_view():
    return render_template('contact.html')


@main_bp.route('/staff')
def staff_view():
    employees = employee_dao.load_all_employee()
    return render_template('staff.html', employees=employees)


#Trang đặt lịch
# --- Bước 1: Thông tin khách hàng ---
@main_bp.route('/booking/step1', methods=['GET', 'POST'])
@user_only_required
def booking_step1():
    form = BookingStep1Form()

    if request.method == 'GET' and current_user.is_authenticated:
        form.name.data = current_user.name
        form.phone_number.data = current_user.phone_number
        form.address.data = current_user.address

    if form.validate_on_submit():
        session['booking'] = {
            'name': form.name.data,
            'phone': form.phone_number.data,
            'email': form.email.data,
            'address': form.address.data
        }
        return redirect(url_for('main_bp.booking_step2'))
    return render_template('booking/booking_step1.html', form=form)

# --- Bước 2: Chọn dịch vụ ---
@main_bp.route('/booking/step2', methods=['GET', 'POST'])
@user_only_required
def booking_step2():
    form = BookingStep2Form()

    # Load tất cả dịch vụ active
    services = Service.query.filter_by(active=True).all()

    # Gán choices (bắt buộc)
    form.services.choices = [(s.id, s.name) for s in services]

    # Load theo category để UI hiển thị
    categories = Category.query.filter_by(active=True).all()

    services_by_category = []
    for c in categories:
        cate_services = [s for s in services if s.category_id == c.id]
        if cate_services:
            services_by_category.append({
                "category": c,
                "services": cate_services
            })

    # GET
    if request.method == "GET":
        return render_template(
            "booking/booking_step2.html",
            form=form,
            categories=services_by_category
        )

    # POST
    if form.validate_on_submit():
        booking_data = session.get("booking", {})
        booking_data["service_ids"] = form.services.data
        session["booking"] = booking_data
        return redirect(url_for("main_bp.booking_step3"))

    # Nếu lỗi
    return render_template(
        "booking/booking_step2.html",
        form=form,
        categories=services_by_category
    )


# --- Bước 3: Chọn nhân viên ---
@main_bp.route('/booking/step3', methods=['GET', 'POST'])
@user_only_required
def booking_step3():
    form = BookingStep3Form()

    # Lấy thông tin dịch vụ đã chọn
    service_ids = session.get('booking', {}).get('service_ids', [])
    services = Service.query.filter(Service.id.in_(service_ids)).all() if service_ids else []
    total_duration = sum(s.duration for s in services) if services else 0

    # Lấy danh sách nhân viên đang làm
    employees = Employee.query.join(User).filter(
        Employee.status == 'Đang làm',
        User.active == True
    ).all()

    # Tạo choices cho form
    form.employee.choices = [(0, "Spa chọn nhân viên phù hợp")]
    for emp in employees:
        if emp.user:  # emp.user là đối tượng User liên kết
            form.employee.choices.append((emp.id, emp.user.username))  # hoặc emp.user.fullname nếu có

    if form.validate_on_submit():
        booking_data = session.get('booking', {})
        booking_data['employee_id'] = form.employee.data
        session['booking'] = booking_data
        session.modified = True
        return redirect(url_for('main_bp.booking_step4'))

    return render_template(
        'booking/booking_step3.html',
        form=form,
        employees=employees,
        services=services,
        total_duration=total_duration
    )


@main_bp.route('/booking/step4', methods=['GET', 'POST'])
@user_only_required
def booking_step4():
    form = BookingStep4Form()
    booking_data = session.get('booking', {})

    # ===== SERVICES =====
    service_ids = booking_data.get('service_ids', [])
    services = Service.query.filter(Service.id.in_(service_ids)).all()

    if not services:
        flash("Vui lòng chọn dịch vụ trước", "danger")
        return redirect(url_for("main_bp.booking_step2"))

    total_duration = sum(s.duration for s in services)
    total_price = sum(s.price for s in services)

    # ===== EMPLOYEE =====
    employee_id = booking_data.get('employee_id')
    employee = Employee.query.get(employee_id) if employee_id not in (None, 0) else None

    # ===== DATE =====
    today = date.today()
    form.appointment_date.choices = [
        (
            (today + timedelta(days=i)).strftime("%Y-%m-%d"),
            (today + timedelta(days=i)).strftime("%d/%m/%Y (%A)")
        )
        for i in range(14)
    ]

    # ===== TIME (DURATION-AWARE) =====
    WORK_START = 9
    WORK_END = 18

    form.appointment_time.choices = [
        (f"{h:02d}:00", f"{h:02d}:00")
        for h in range(WORK_START, WORK_END)
        if h * 60 + total_duration <= WORK_END * 60
    ]

    # ===== POST =====
    if request.method == "POST":

        if not form.appointment_time.data:
            flash("Vui lòng chọn giờ hẹn", "danger")
            return redirect(url_for("main_bp.booking_step4"))

        appointment_date = datetime.strptime(
            form.appointment_date.data, "%Y-%m-%d"
        ).date()

        appointment_time = datetime.strptime(
            form.appointment_time.data, "%H:%M"
        ).time()

        selected_employee_id = employee_id

        # AUTO ASSIGN CHỈ Ở ĐÂY
        if selected_employee_id == 0:
            selected_employee_id = auto_assign_employee(
                appointment_date,
                appointment_time,
                [s.duration for s in services]
            )

            if not selected_employee_id:
                flash("Không có nhân viên phù hợp cho khung giờ này", "danger")
                return redirect(url_for("main_bp.booking_step4"))

        # CHECK TẠM (FINAL CHECK Ở STEP 5)
        valid, message = is_booking_valid(
            selected_employee_id,
            appointment_date,
            appointment_time,
            [s.duration for s in services]
        )

        if not valid:
            flash(message, "danger")
            return redirect(url_for("main_bp.booking_step4"))

        booking_data.update({
            'date': form.appointment_date.data,
            'time': form.appointment_time.data,
            'employee_id': selected_employee_id
        })

        session['booking'] = booking_data
        session.modified = True

        return redirect(url_for("main_bp.booking_confirmation"))

    return render_template(
        "booking/booking_step4.html",
        form=form,
        services=services,
        total_duration=total_duration,
        total_price=total_price,
        employee=employee
    )


@main_bp.route('/booking/confirmation', methods=['GET', 'POST'])
@user_only_required
def booking_confirmation():
    form = BookingConfirmForm()
    booking_data = session.get('booking')

    # ===== VALIDATE SESSION =====
    if not booking_data:
        flash("Vui lòng đặt lịch lại từ đầu", "danger")
        return redirect(url_for('main_bp.booking_step1'))

    required_keys = ['date', 'time', 'service_ids', 'employee_id']
    if not all(k in booking_data for k in required_keys):
        flash("Dữ liệu đặt lịch không hợp lệ", "danger")
        return redirect(url_for('main_bp.booking_step1'))

    # ===== SERVICES =====
    services = Service.query.filter(
        Service.id.in_(booking_data['service_ids'])
    ).all()

    if not services:
        flash("Không có dịch vụ hợp lệ", "danger")
        return redirect(url_for('main_bp.booking_step2'))

    service_durations = [s.duration for s in services]
    total_duration = sum(service_durations)
    total_price = sum(s.price for s in services)

    appointment_date = datetime.strptime(
        booking_data['date'], "%Y-%m-%d"
    ).date()

    appointment_time = datetime.strptime(
        booking_data['time'], "%H:%M"
    ).time()

    # ===== EMPLOYEE =====
    employee_id = booking_data['employee_id']

    # Auto assign nếu spa chọn
    if employee_id == 0:
        employee_id = auto_assign_employee(
            appointment_date,
            appointment_time,
            service_durations
        )

        if not employee_id:
            flash("Không có nhân viên trống trong khung giờ này", "danger")
            return redirect(url_for('main_bp.booking_step4'))

    employee = Employee.query.get(employee_id)

    # ===== CUSTOMER (THEO MODEL USER) =====
    customer = None
    if current_user.is_authenticated:
        customer = {
            "name": current_user.name,
            "phone": current_user.phone_number,
            "address": current_user.address
        }

    # ===== POST: FINAL CHECK & SAVE =====
    if form.validate_on_submit():
        valid, message = is_booking_valid(
            employee_id,
            appointment_date,
            appointment_time,
            service_durations
        )

        if not valid:
            flash(message, "danger")
            return redirect(url_for('main_bp.booking_step4'))

        try:
            booking = Booking(
                customer_id=current_user.id,
                staff_id=employee_id,
                date=appointment_date,
                time=appointment_time,
                status=BookingStatus.PENDING,
                notes=form.notes.data,
                total_price=total_price
            )

            for s in services:
                booking.services.append(s)

            db.session.add(booking)
            db.session.commit()

            session.pop('booking', None)

            return render_template(
                'booking/booking_success.html',
                booking=booking,
                services=services
            )

        except Exception as e:
            db.session.rollback()
            flash("Có lỗi khi lưu đặt lịch", "danger")
            return redirect(url_for('main_bp.booking_step4'))

    return render_template(
        'booking/booking_confirmation.html',
        form=form,
        services=services,
        employee=employee,
        customer=customer,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        total_duration=total_duration,
        total_price=total_price
    )



#Trang xem lịch đã đặt
@main_bp.route('/order')
@user_only_required
def booking_history():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_bp.login_view'))

    bookings = Booking.query.filter_by(customer_id=current_user.id) \
        .order_by(Booking.created_date.desc()) \
        .all()

    return render_template('booking/booking_history.html', bookings=bookings)


@main_bp.route('/order/<int:booking_id>')
@user_only_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Ngăn user xem booking của người khác
    if booking.customer_id != current_user.id:
        return "Bạn không có quyền xem lịch này", 403

    return render_template('booking/booking_detail.html', booking=booking)
