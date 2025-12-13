import datetime
from datetime import date, timedelta


from flask import render_template, Blueprint, request, redirect, session, jsonify, url_for, flash
from flask_login import login_required, current_user
import math

from spa_app import db
from spa_app.dao.user_dao import get_age_user, change_password
from spa_app.dao import services_dao, user_dao, employee_dao
from spa_app.forms.booking_form import BookingConfirmForm, BookingStep4Form, BookingStep3Form, BookingStep2Form, \
    BookingStep1Form
from spa_app.models import Setting, Booking, User, BookingStatus, Service, Employee, Category  # THÊM Category

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
    return render_template('services/services.html', services=services,
                           pages=pages, current_page=page, categories=categories)


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

    return render_template('services/service-detail.html', service=services_dao.get_service_by_id(id))



@main_bp.route('/contact')
def contact_view():
    return render_template('contact.html')


@main_bp.route('/staff')
def staff_view():
    employees = employee_dao.load_all_employee()
    return render_template('staff.html', employees=employees)


# --- Bước 1: Thông tin khách hàng ---
@main_bp.route('/booking/step1', methods=['GET', 'POST'])
def booking_step1():
    form = BookingStep1Form()
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

#--- Bước 4: Chọn ngày giờ ---
@main_bp.route('/booking/step4', methods=['GET', 'POST'])
def booking_step4():
    form = BookingStep4Form()

    booking_data = session.get('booking', {})
    service_ids = booking_data.get('service_ids', [])

    services = Service.query.filter(Service.id.in_(service_ids)).all() if service_ids else []

    total_duration = sum(s.duration for s in services)
    total_price = sum(s.price for s in services)

    # ===== DANH SÁCH NGÀY (KHÔNG QUÁ KHỨ) =====
    today = date.today()
    days = []
    for i in range(14):
        d = today + datetime.timedelta(days=i)
        days.append((d.strftime("%Y-%m-%d"), d.strftime("%d/%m/%Y (%A)")))

    # ⚠️ GÁN CHO FORM TRƯỚC validate
    form.appointment_date.choices = days

    # ===== DANH SÁCH GIỜ =====
    hours = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(9, 18)]
    form.appointment_time.choices = hours

    # ===== POST =====
    if request.method == "POST":
        if not form.appointment_time.data:
            flash("Vui lòng chọn giờ hẹn", "danger")
            return redirect(url_for("main_bp.booking_step4"))

        booking_data['date'] = form.appointment_date.data
        booking_data['time'] = form.appointment_time.data

        session['booking'] = booking_data
        session.modified = True

        return redirect(url_for('main_bp.booking_confirmation'))

    return render_template(
        'booking/booking_step4.html',
        form=form,
        services=services,
        total_duration=total_duration,
        total_price=total_price
    )


# --- Bước 5: Xác nhận ---
@main_bp.route('/booking/confirmation', methods=['GET', 'POST'])
def booking_confirmation():
    form = BookingConfirmForm()
    booking_data = session.get('booking')

    if not booking_data:
        return redirect(url_for('main_bp.booking_step1'))

    # Lấy thông tin từ session
    service_ids = booking_data.get('service_ids', [])
    services = Service.query.filter(Service.id.in_(service_ids)).all() if service_ids else []
    employee_id = booking_data.get('employee_id')
    employee = Employee.query.get(employee_id) if employee_id and employee_id != 0 else None

    # Tính tổng
    total_duration = sum(s.duration for s in services) if services else 0
    total_price = sum(s.price for s in services) if services else 0

    # Thông tin customer
    customer_info = {
        'name': booking_data.get('name'),
        'phone': booking_data.get('phone'),
        'email': booking_data.get('email'),
        'address': booking_data.get('address')
    }

    # === THÊM: VALIDATION CUỐI CÙNG TRƯỚC KHI HIỂN THỊ ===
    validation_errors = []

    if employee_id and employee_id != 0:
        try:
            appointment_date = datetime.datetime.strptime(booking_data['date'], "%Y-%m-%d").date()
            appointment_time = datetime.datetime.strptime(booking_data['time'], "%H:%M").time()

            # 1. Kiểm tra giới hạn 5 khách/ngày
            setting = Setting.query.first()
            max_bookings = setting.max_booking_per_day if setting else 5

            bookings_count = Booking.query.filter_by(
                staff_id=employee_id,
                date=appointment_date
            ).filter(
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            ).count()

            if bookings_count >= max_bookings:
                validation_errors.append(f"⚠️ Nhân viên đã có {bookings_count}/{max_bookings} khách trong ngày này")

            # 2. Kiểm tra trùng thời gian
            existing_booking = Booking.query.filter_by(
                staff_id=employee_id,
                date=appointment_date,
                time=appointment_time
            ).filter(
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            ).first()

            if existing_booking:
                validation_errors.append(f"⏰ Thời gian {appointment_time.strftime('%H:%M')} đã được đặt")

        except Exception as e:
            validation_errors.append(f"❌ Lỗi kiểm tra: {str(e)}")

    # Nếu có lỗi validation, redirect về bước 3
    if validation_errors:
        for error in validation_errors:
            flash(error, "danger")
        return redirect(url_for('main_bp.booking_step3'))

    if form.validate_on_submit():
        # === KIỂM TRA LẠI LẦN CUỐI TRƯỚC KHI LƯU
        if employee_id and employee_id != 0:
            try:
                appointment_date = datetime.datetime.strptime(booking_data['date'], "%Y-%m-%d").date()
                appointment_time = datetime.datetime.strptime(booking_data['time'], "%H:%M").time()

                # Kiểm tra lại giới hạn
                setting = Setting.query.first()
                max_bookings = setting.max_booking_per_day if setting else 5

                bookings_count = Booking.query.filter_by(
                    staff_id=employee_id,
                    date=appointment_date
                ).filter(
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                ).count()

                if bookings_count >= max_bookings:
                    flash(f"❌ Nhân viên đã đầy lịch ({bookings_count}/{max_bookings} khách). Vui lòng đặt lại.",
                          "danger")
                    return redirect(url_for('main_bp.booking_step3'))

                # Kiểm tra lại trùng thời gian
                existing_booking = Booking.query.filter_by(
                    staff_id=employee_id,
                    date=appointment_date,
                    time=appointment_time
                ).filter(
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                ).first()

                if existing_booking:
                    flash(f"⏰ Thời gian này đã có khách đặt. Vui lòng chọn giờ khác.", "danger")
                    return redirect(url_for('main_bp.booking_step4'))

            except Exception as e:
                flash(f"❌ Lỗi hệ thống: {str(e)}", "danger")
                return redirect(url_for('main_bp.booking_step4'))

        # Tạo booking
        booking = Booking(
            customer_id=current_user.id if current_user.is_authenticated else None,
            staff_id=employee_id if employee_id != 0 else None,
            date=datetime.datetime.strptime(booking_data['date'], "%Y-%m-%d").date(),
            time=datetime.datetime.strptime(booking_data['time'], "%H:%M").time(),
            status=BookingStatus.PENDING,
            notes=form.notes.data,
            total_price=total_price
        )

        # Thêm dịch vụ
        for service in services:
            booking.services.append(service)

        db.session.add(booking)
        db.session.commit()

        # Clear session
        session.pop('booking', None)

        return render_template('booking/booking_success.html',
                               booking=booking,
                               services=services)

    # Truyền validation errors cho template để hiển thị cảnh báo
    return render_template('booking/booking_confirmation.html',
                           form=form,
                           customer=customer_info,
                           services=services,
                           employee=employee,
                           time_data={
                               'date': booking_data.get('date'),
                               'time': booking_data.get('time')
                           },
                           summary={
                               'total_duration': total_duration,
                               'total_price': total_price
                           },
                           validation_errors=validation_errors)


@main_bp.route('/order')
def booking_history():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_bp.login_view'))

    bookings = Booking.query.filter_by(customer_id=current_user.id)\
                            .order_by(Booking.created_date.desc())\
                            .all()

    return render_template('booking/booking_history.html', bookings=bookings)

@main_bp.route('/order/<int:booking_id>')
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Ngăn user xem booking của người khác
    if booking.customer_id != current_user.id:
        return "Bạn không có quyền xem lịch này", 403

    return render_template('booking/booking_detail.html', booking=booking)


