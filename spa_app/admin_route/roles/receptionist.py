from wtforms.fields.choices import SelectField

from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from flask_admin.contrib.sqla import ModelView
from spa_app.admin_route.roles.admin import Admin
from spa_app.models import UserRole, Service, db, BookingStatus, Booking, PaymentStatus


class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.RECEPTIONIST

class MyReceptionistIndexView(base.BaseIndexView):
    required_role = UserRole.RECEPTIONIST

class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_edit = False
    can_delete = False
    can_export = True

class MyBookingView(AuthenticatedView):

    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'notes', 'total_price'
    )

    exclude_columns = ('payment', 'booking_services')
    form_excluded_columns = ('payment', 'booking_services')
    form_columns = ('status',)
    form_overrides = {
        'status': SelectField
    }

    form_args = {
        'status': {
            'choices': [
                (BookingStatus.PENDING.value, 'Pending'),
                (BookingStatus.CONFIRMED.value, 'Confirmed'),
                (BookingStatus.CANCELED.value, 'Canceled')
            ],
        }
    }

    # column_extra_row_actions = [
    #     EndpointLinkRowAction(
    #         'fa fa-print',
    #         # 'print_booking',
    #         id_arg='booking_id'
    #     )
    # ]

    def get_query(self):
        query = super().get_query()
        return query.filter(
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELED,
                PaymentStatus.UNPAID
            ])
        )

    def get_count_query(self):
        query = super().get_count_query()
        return query.filter(
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELED,
            ]),
            Booking.payment == PaymentStatus.UNPAID
        )



def init_receptionist(app):
    receptionist_index = MyReceptionistIndexView(url="/receptionist/", endpoint="receptionist_index", name="Thông tin")
    receptionist = Admin(
        app,
        name="Beauty Spa - Cashier",
        theme=Bootstrap4Theme(),
        endpoint="receptionist_index",
        index_view=receptionist_index,
        url="/receptionist"
    )
    receptionist.add_view(MyServiceView(Service, db.session, name='Dịch vụ', endpoint='service_receptionist'))
    receptionist.add_view(MyBookingView(Booking, db.session, name='Lịch đã đặt', endpoint='booking_receptionist'))
    receptionist.add_view(base.BaseLogoutView("Đăng xuất", endpoint="receptionise_logout"))