from flask import url_for, make_response, current_app, abort
from flask_login import current_user, login_required
from markupsafe import Markup
from sqlalchemy.testing.util import total_size
from wtforms.fields.choices import SelectField
from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from spa_app.admin_route.roles.admin import Admin
from spa_app.auth_route.routes import admin_bp
from spa_app.dao import services_dao
from spa_app.models import UserRole, Service, db, PaymentStatus, Booking, BookingStatus, DiscountStatus


class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.CASHIER


class MyCashierIndexView(base.BaseIndexView):
    required_role = UserRole.CASHIER


class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_edit = False  # chỉ chỉnh sửa thông tin cá nhân
    can_delete = False
    can_export = True


def FormatDiscountValue(view, context, model, name):
    if model.discount_type == DiscountStatus.DISCOUNT:
        return model.discount_value
    return Markup('<span class="text-muted">—</span>')


def PrintPaymentReceiptPDF(view, context, model, name):
    if model.payment == PaymentStatus.PAID:
        url = url_for(
            'admin_bp.export_payment_pdf',
            booking_id=model.id
        )
        return Markup(
            f'<a class="btn btn-sm btn-success" href="{url}" target="_blank">In phiếu thanh toán</a>'
        )
    return ""


class MyBookingView(AuthenticatedView):
    can_create = False
    can_delete = False
    can_export = False
    can_edit = True

    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'payment', 'notes',
        'total_price', 'discount_type', 'discount_value',
        'print_payment_pdf'
    )

    column_formatters = {
        'discount_value': FormatDiscountValue,
        'print_payment_pdf': PrintPaymentReceiptPDF,
    }

    column_labels = {
        'customer': 'Khách hàng',
        'staff': 'Nhân viên',
        'date': 'Ngày đặt',
        'time': 'Thời gian đặt',
        'status': 'Tình trạng lịch hẹn',
        'payment': 'Thanh toán',
        'notes': 'Ghi chú',
        'total_price': 'Tổng tiền',
        'discount_type': 'Giảm giá',
        'discount_value': 'Giá trị giảm',
    }

    form_columns = ('payment', 'discount_type', 'discount_value')

    form_overrides = {
        'discount_type': SelectField,
        'payment': SelectField,

    }

    form_args = {
        'payment': {
            'choices': [
                (PaymentStatus.UNPAID.value, 'Chưa thanh toán'),
                (PaymentStatus.PAID.value, 'Đã thanh toán')
            ],
            'coerce': str
        },

        'discount_type': {
            'choices': [
                (DiscountStatus.NONE.value, 'Không có mã giảm giá'),
                (DiscountStatus.DISCOUNT.value, 'Có mã giảm giá'),
            ],
            'coerce': str
        }
    }

    def get_query(self):
        query = super().get_query()
        return query.filter(
            Booking.status.in_([
            BookingStatus.COMPLETED,
        ])
    )


    def get_count_query(self):
        query = super().get_count_query()
        return query.filter(
            Booking.status.in_([
            BookingStatus.COMPLETED,
        ])
    )


def init_cashier(app):
    from spa_app.dao import booking_dao, user_dao
    from spa_app.filters import format_currency

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
        # Chặn role
        if current_user.role != UserRole.CASHIER:
            abort(403)

        # Chặn trạng thái
        if booking.status != BookingStatus.COMPLETED:
            abort(403)

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

    # View chính cashier
    cashier_index = MyCashierIndexView(url="/cashier/", endpoint="cashier_index", name="Thông tin")
    cashier = Admin(
        app,
        name="Beauty Spa - Cashier",
        theme=Bootstrap4Theme(),
        endpoint="cashier_index",
        index_view=cashier_index,
        url="/cashier"
    )

    # Thêm các view
    cashier.add_view(MyServiceView(Service, db.session, name='Dịch vụ', endpoint='service_cashier'))
    cashier.add_view(MyBookingView(Booking, db.session, name='Lịch đã đặt', endpoint="booking_cashier"))
    cashier.add_view(base.BaseLogoutView("Đăng xuất", endpoint="cashier_logout"))
