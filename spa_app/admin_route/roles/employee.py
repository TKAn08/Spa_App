
from flask import url_for, make_response, abort
from flask_login import login_required, current_user
from markupsafe import Markup
from wtforms.fields.choices import SelectField

from spa_app.auth_route.routes import admin_bp
from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from spa_app.admin_route.roles.admin import Admin
from spa_app.dao import services_dao
from spa_app.models import UserRole, BookingStatus, Booking, db, PaymentStatus


class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.EMPLOYEE

class MyEmployeeIndexView(base.BaseIndexView):
    required_role = UserRole.EMPLOYEE

class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_edit = False  # chỉ chỉnh sửa thông tin cá nhân
    can_delete = False
    can_export = True


def PrintBookingPDF(view, context, model, name):
    if model.status == BookingStatus.COMPLETED:
        url = url_for(
            "admin_bp.export_booking_pdf",
            booking_id=model.id
        )
        return Markup(
            f'<a class="btn btn-sm btn-info" href="{url}" target="_blank">In phiếu dịch vụ</a>'
        )
    return ""

class MyBookingView(AuthenticatedView):
    can_create = False
    can_delete = False
    can_export = False

    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'payment', 'notes', 'total_price', 'print_booking_pdf'
    )

    exclude_columns = ('booking_services',)
    form_columns = ('status',)

    form_overrides = {
        'status': SelectField
    }
    form_args = {
        'status': {
            'choices': [
                (BookingStatus.COMPLETED.value, 'Completed'),
                (BookingStatus.CANCELED.value, 'Canceled')
            ],
        }
    }
    column_formatters = {
        'print_booking_pdf': PrintBookingPDF
    }

    column_labels = {
        'print_booking_pdf': 'Phiếu dịch vụ'
    }
    form_excluded_columns = ('payment', 'booking_services', 'status')
    def get_query(self):
        query = super().get_query()
        return query.filter(
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.COMPLETED,
            ])
        )

    #Load lại paginate
    def get_count_query(self):
        query = super().get_count_query()
        return query.filter(
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.COMPLETED,
            ]),
            Booking.payment == PaymentStatus.UNPAID
        )




def init_employee(app):

    from spa_app.dao import booking_dao, user_dao
    from spa_app.filters import format_currency
    @admin_bp.route("/booking/<int:booking_id>/booking-sheet")
    @login_required
    def export_booking_pdf(booking_id):
        booking = booking_dao.get_booking_by_id(booking_id)
        services_in_booking = services_dao.get_services_in_booking(booking.id)

        #Tạo biến mới để hiển thị giá trị string currency dưới dạng VND
        for s in services_in_booking:
            s.price_display = format_currency(s.price)

        age = user_dao.get_age_user(current_user.DOB)
        # Chặn role
        if current_user.role != UserRole.EMPLOYEE:
            abort(403)

        # Chặn trạng thái
        if booking.status != BookingStatus.COMPLETED:
            abort(403)

        #Tạo pdf
        from spa_app.export_file import export_pdf_from_url
        pdf = export_pdf_from_url(
            'booking_pdf/service_order_pdf.html',
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


    employee_index = MyEmployeeIndexView(url="/employee/", endpoint="employee_index", name="Thông tin")
    employee = Admin(
        app,
        name="Beauty Spa - Cashier",
        theme=Bootstrap4Theme(),
        endpoint="employee_index",
        index_view=employee_index,
        url="/employee"
    )
    employee.add_view(MyBookingView(Booking, db.session, name='Lịch đã đặt', endpoint="booking_employee"))
    employee.add_view(base.BaseLogoutView("Đăng xuất", endpoint="employee_logout"))
