from flask_admin import AdminIndexView, expose, BaseView
from flask import redirect, url_for, make_response, current_app
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user, login_required
from datetime import date

from markupsafe import Markup

from spa_app.auth_route.routes import admin_bp
from spa_app.dao import user_dao, booking_dao, services_dao
from spa_app.filters import format_currency
from spa_app.models import Booking, BookingStatus, PaymentStatus, UserRole, DiscountStatus


class BaseAuthenticatedView(ModelView):
    required_role = None

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.role == self.required_role

    def inaccessible_callback(self, name, **kwargs):
        # Chỉ redirect nếu chưa login
        if not current_user.is_authenticated:
            return redirect(url_for('admin-login'))  # login chung
        # Nếu login nhưng role không đúng, có thể trả 403 thay vì redirect
        from flask import abort
        return abort(403)


# Dùng cho employee và cashier
def filter_today(query):
    return query.filter(
        Booking.date == date.today()
    )


# Dùng cho receptionist
def filter_from_today(query):
    return query.filter(
        Booking.date >= date.today()
    )


def print_pdf_button_formatter(text, link):
    def _formatter(view, context, model, name):
        if model.payment == PaymentStatus.PAID or model.status == BookingStatus.CONFIRMED:
            url = url_for(
                link,
                booking_id=model.id
            )
            return Markup(
                f'''
                <a class="badge btn btn-secondary
                           d-flex justify-content-center align-items-center"
                   href="{url}"
                   target="_blank"
                   style="
                       white-space: nowrap;
                       height: 50px;
                       min-width: 160px;
                       font-size: 0.9rem;
                   ">
                    {text}
                </a>
                '''
            )
        return ""

    return _formatter


def format_status(text, color):
    return Markup(
        f'''
        <span class="badge bg-{color}"
              style="display:flex;
                     height: 50px;
                     color: white;
                     align-items: center;
                     justify-content: center;
                     font-size:0.9rem;">
            {text}
        </span>
        '''

    )


def format_booking_status(view, context, model, name):
    if model.status == BookingStatus.PENDING:
        return format_status("Chờ xác nhận", "secondary")
    elif model.status == BookingStatus.CONFIRMED:
        return format_status("Đã xác nhận", "info")
    elif model.status == BookingStatus.COMPLETED:
        return format_status("Hoàn thành", "success")
    elif model.status == BookingStatus.CANCELED:
        return format_status("Đã huỷ", "danger")
    return model.status.name


class BaseIndexView(AdminIndexView):
    required_role = None

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect("/admin-login")
        if current_user.role != self.required_role:
            from flask import abort
            return abort(403)

        from spa_app.dao import user_dao, services_dao
        user = user_dao.get_user_by_id(current_user.id)
        age = user_dao.get_age_user(user.DOB)
        stats = services_dao.category_stats()

        return self.render('admin/information.html', age=age, user=user, stats=stats)

    @property
    def menu_title(self):
        return "Thông tin"


class BaseLogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin-login")

    def is_accessible(self):
        return current_user.is_authenticated


class BaseServiceView(ModelView):
    column_list = ('name', 'image', 'price', 'category', 'description')
    column_searchable_list = ['name']
    column_filters = ['name']
    column_labels = {
        'name': "Tên Dịch vụ",
        'image': "Hình ảnh",
        'price': "Giá",
        'category': "Loại",
        'description': "Mô tả"
    }



@admin_bp.route("/booking_payment/<int:booking_id>/booking_payment-sheet")
@login_required
def export_payment_pdf(booking_id):
    booking = booking_dao.get_booking_by_id(booking_id)
    services_in_booking = services_dao.get_services_in_booking(booking.id)
    VAT_Rate = current_app.config.get('VAT_RATE') or 0

    booking.sum = [0] * 4
    booking.sum_display = [format_currency(0)] * 4

    for s in services_in_booking:
        s_price = s.price or 0

        # Giá gốc
        s.price_display = format_currency(s_price)
        booking.sum[0] += s_price
        booking.sum_display[0] = format_currency(booking.sum[0])

        # VAT
        s.VAT = s_price * VAT_Rate / 100
        s.VAT_display = format_currency(s.VAT)
        booking.sum[1] += s.VAT
        booking.sum_display[1] = format_currency(booking.sum[1])

        # Giảm giá
        discount_value = booking.discount_value or 0
        s.price_in_discount = s_price * discount_value / 100 \
            if booking.discount_type != DiscountStatus.NONE and discount_value else 0
        s.price_in_discount_display = format_currency(s.price_in_discount)
        booking.sum[2] += s.price_in_discount
        booking.sum_display[2] = format_currency(booking.sum[2])

        # Tổng tiền dịch vụ
        s.total_price = s_price - s.price_in_discount + s.VAT
        s.total_price_display = format_currency(s.total_price)

        # Tổng tiền tất cả dịch vụ
        booking.sum[3] += s.total_price
        booking.sum_display[3] = format_currency(booking.sum[3])

    age = user_dao.get_age_user(current_user.DOB)

    # Tạo pdf
    from spa_app.export_file import export_pdf_from_url
    pdf = export_pdf_from_url(
        'booking_pdf/payment_pdf.html',
        booking=booking,
        services_in_booking=services_in_booking,
        age=age
    )

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Disposition"] = (
        f"inline; filename=booking_{booking_id}.pdf"
    )
    return response
