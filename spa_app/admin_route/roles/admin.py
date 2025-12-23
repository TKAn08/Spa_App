from datetime import datetime

from markupsafe import Markup
from sqlalchemy import extract, or_

from spa_app.admin_route import base
from flask_admin import Admin, expose, BaseView
from spa_app.admin_route.base import BaseLogoutView
from spa_app.dao import services_dao, employee_dao
from spa_app.models import UserRole, User, Service, Category, Booking, db, PaymentStatus, DiscountStatus, BookingStatus
from wtforms.fields.simple import TextAreaField, PasswordField
from wtforms.widgets import TextArea
from flask_admin.theme import Bootstrap4Theme

class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.ADMIN

class MyAdminIndexView(base.BaseIndexView):
    required_role = UserRole.ADMIN

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class MyUserView(AuthenticatedView):
    form_extra_fields = {
        'password': PasswordField('Password'),
    }
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_hash_password(form.password.data)
        return super().on_model_change(form, model, is_created)

class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_export = True
    extra_js =  ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'description': CKTextAreaField
    }

class MyCategoryView(AuthenticatedView):
    column_list = ['name', 'products', 'description']
    column_searchable_list = ['name']
    column_filters = ['name']

    column_labels = {
        'name': "Tên Dịch vụ",
        'products': 'Các dịch vụ',
        'description': "Mô tả"
    }

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
    can_export = True
    column_default_sort = ('created_date', True)
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

    def get_query(self):
        query = super().get_query()
        query = base.filter_from_today(query)
        return query

    def get_count_query(self):
        query = super().get_count_query()
        query = base.filter_from_today(query)
        return query


class MyBookingHistoryView(AuthenticatedView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    actions = None

    column_default_sort = ('created_date', True)

    column_filters = (
        'status',
        'payment',
        'created_date'
    )

    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'payment', 'final_price', 'print_payment_pdf'
    )

    column_formatters = {
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
        'final_price': 'Thành tiền',
        'created_date': 'Ngày đặt lịch',
        'print_payment_pdf': 'In phiếu thanh toán'
    }

    def get_query(self):
        query = super().get_query()

        #Lọc theo năm hiện tại
        current_year = datetime.now().year
        query = query.filter(extract('year', Booking.created_date) == current_year)

        #Lọc theo trạng thái lịch chỉ lấy Booking đã thanh toán hoặc bị hủy
        query = query.filter(
            or_(
                Booking.payment == PaymentStatus.PAID,
                Booking.status == BookingStatus.CANCELED
            )
        )

        return query

    def get_count_query(self):
        query = super().get_count_query()

        # Lọc theo năm hiện tại
        current_year = datetime.now().year
        query = query.filter(extract('year', Booking.created_date) == current_year)

        # Lọc theo trạng thái lịch chỉ lấy Booking đã thanh toán hoặc bị hủy
        query = query.filter(
            or_(
                Booking.payment == PaymentStatus.PAID,
                Booking.status == BookingStatus.CANCELED
            )
        )

        return query



class MyReportView(BaseView):
    @expose('/')
    def index(self, **kwargs):
        return self.render('admin/reports.html')

def init_admin(app):
    from spa_app.dao import booking_dao
    from spa_app.filters import format_currency, format_date_vietnamese


    @app.context_processor
    def inject_admin_stats():
        booking_in_month = booking_dao.count_bookings_in_month()
        booking_in_day = booking_dao.count_bookings_in_day()
        completed_booking_in_month = booking_dao.count_completed_booking_in_month()
        pending_booking_in_month = booking_dao.count_pending_booking_in_month()
        canceled_booking_in_month = booking_dao.count_canceled_booking_in_month()
        revenue_in_month = format_currency(booking_dao.get_revenue_in_month())
        revenue_in_day = format_currency(booking_dao.get_revenue_in_day())
        get_current_count_customer = booking_dao.get_current_count_customer()
        get_current_count_employee = booking_dao.get_current_count_employee()
        get_revenue_each_day_in_week = format_date_vietnamese(booking_dao.get_revenue_each_day_in_week())
        get_top_3_services_in_month = services_dao.get_top_3_services_in_month()
        get_top_5_best_staff_in_month = employee_dao.get_top_5_best_employee_in_month()
        return dict(
            booking_in_month=booking_in_month,
            booking_in_day=booking_in_day,
            completed_booking_in_month=completed_booking_in_month,
            pending_booking_in_month=pending_booking_in_month,
            canceled_booking_in_month=canceled_booking_in_month,
            revenue_in_month=revenue_in_month,
            revenue_in_day=revenue_in_day,
            get_current_count_customer=get_current_count_customer,
            get_current_count_employee=get_current_count_employee,
            get_revenue_each_day_in_week=get_revenue_each_day_in_week,
            get_top_3_services_in_month=get_top_3_services_in_month,
            get_top_5_best_staff_in_month=get_top_5_best_staff_in_month
        )

    # ----------------- ADMIN PANEL -----------------
    admin_index = MyAdminIndexView(url="/admin/", endpoint="admin_index", name="Thông tin")
    admin = Admin(
        app,
        name="Beauty Spa - Admin",
        theme=Bootstrap4Theme(),
        endpoint="admin_index",
        index_view=admin_index,
        url="/admin"
    )
    admin.add_view(MyUserView(User, db.session, name="Tài khoản người dùng"))
    admin.add_view(MyCategoryView(Category, db.session, name='Loại dịch vụ'))
    admin.add_view(MyBookingView(Booking, db.session, name='Lịch đã đặt', endpoint="booking_admin"))
    admin.add_view(MyServiceView(Service, db.session, name='Dịch vụ', endpoint='service_admin'))
    admin.add_view(MyReportView(name='Thống kê'))
    admin.add_view(MyBookingHistoryView(Booking, db.session, name="Lịch sử đặt lịch"))
    admin.add_view(BaseLogoutView("Đăng xuất", endpoint="admin_logout"))