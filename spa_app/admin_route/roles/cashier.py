
from flask import current_app, flash, abort
from markupsafe import Markup

from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from spa_app.admin_route.roles.admin import Admin
from spa_app.dao.booking_dao import validate_discount_value
from spa_app.models import UserRole, Service, db, PaymentStatus, Booking, BookingStatus, DiscountStatus


class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.CASHIER


class MyCashierIndexView(base.BaseIndexView):
    required_role = UserRole.CASHIER


class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_delete = False
    can_export = True
    can_edit = False


def FormatDiscountValue(view, context, model, name):
    if model.discount_type == DiscountStatus.DISCOUNT:
        return model.discount_value
    return Markup('<span class="text-muted">—</span>')



def format_payment_status(view, context, model, name):
    if model.payment == PaymentStatus.UNPAID:
        return base.format_status("Chưa thanh toán", "warning")
    elif model.payment == PaymentStatus.PAID:
        return base.format_status("Đã thanh toán", "success")
    return model.payment.name


class MyBookingView(AuthenticatedView):
    can_create = False
    can_delete = False
    can_export = False
    column_default_sort = ('created_date', True)

    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'payment', 'notes',
        'total_price', 'discount_type', 'discount_value',
        'discount_amount', 'final_price',
        'print_payment_pdf'
    )

    column_formatters = {
        'discount_value': FormatDiscountValue,
        'print_payment_pdf': base.print_pdf_button_formatter("Phiếu thanh toán", 'admin_bp.export_payment_pdf'),
        'status': base.format_booking_status,
        'payment': format_payment_status,
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
        'discount_value': 'Giá trị giảm giá (%)',
        'discount_amount': 'Tiền giảm giá',
        'final_price': 'Thành tiền',
        'print_payment_pdf': 'In phiếu thanh toán'
    }

    form_columns = ('payment', 'discount_type', 'discount_value')

    def on_model_change(self, form, model, is_created):

        if model.discount_type == DiscountStatus.NONE:
            model.discount_amount = 0
        else:
            validate_discount_value(model.discount_value)
            model.discount_amount = model.total_price * float(model.discount_value) / 100

        vat_rate = current_app.config.get("VAT_RATE", 0)
        model.final_price = (
                model.total_price
                + model.total_price * vat_rate / 100
                - model.discount_amount
        )

    def on_form_prefill(self, form, id):
        model = self.get_one(id)
        if model.payment == PaymentStatus.PAID:
            flash("Đơn hàng đã hoàn thành, không thể chỉnh sửa!", "warning")
            for field_name, field in form._fields.items():
                field.render_kw = {"disabled": True}

    def get_query(self):
        query = super().get_query()
        query = base.filter_today(query)
        return query.filter(
            Booking.status.in_([BookingStatus.COMPLETED,])
        )

    def get_count_query(self):
        query = super().get_count_query()
        query = base.filter_today(query)
        return query.filter(
            Booking.status.in_([BookingStatus.COMPLETED,])
        )


def init_cashier(app):

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
