from wtforms.fields.choices import SelectField
from flask_admin.contrib.sqla import ModelView
from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from spa_app.admin_route.roles.admin import Admin
from spa_app.models import UserRole, BookingStatus, Booking, db


class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.EMPLOYEE

class MyEmployeeIndexView(base.BaseIndexView):
    required_role = UserRole.EMPLOYEE

class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_edit = False  # chỉ chỉnh sửa thông tin cá nhân
    can_delete = False
    can_export = True


class MyBookingView(ModelView):
    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'notes', 'total_price'
    )

    exclude_columns = ('payment', 'booking_services')
    form_excluded_columns = ('payment', 'booking_services')

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

    def get_query(self):
        query = super().get_query()
        return query.filter(
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.COMPLETED,
            ])
        )

    def get_count_query(self):
        query = super().get_count_query()
        return query.filter(
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.COMPLETED,
            ])
        )


def init_employee(app):
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
