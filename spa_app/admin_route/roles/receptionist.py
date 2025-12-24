from datetime import datetime

from flask import request

from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
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
    can_create = False
    can_delete = False
    can_export = False
    column_default_sort = ('created_date', True)
    column_filters = ['date']  # sẽ cho phép filter theo ngày trong UI
    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'status', 'notes', 'total_price'
    )


    column_formatters = {
        'status': base.format_booking_status,
    }

    column_labels = {
        'id': 'Mã đặt hàng',
        'customer': 'Khách hàng',
        'staff': 'Nhân viên',
        'date': 'Ngày đặt',
        'time': 'Giờ đặt',
        'status': 'Tình trạng',
        'notes': 'Ghi chú',
        'total_price': 'Tạm tính'
    }

    form_columns = ('status',)


    def get_query(self):
        query = super().get_query()
        query = base.filter_from_today(query)
        return query.filter(
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELED,
            ]),
            Booking.payment == PaymentStatus.UNPAID
        )

    def get_count_query(self):
        query = super().get_count_query()
        query = base.filter_from_today(query)
        return query.filter(
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELED,
            ]),
            Booking.payment == PaymentStatus.UNPAID
        )


class MyEmployeeWorkScheduleView(AuthenticatedView):
    can_create = False
    can_edit = True
    column_filters = ['date']
    #
    column_searchable_list = ['staff.name']
    #Sắp xếp theo thời gian lịch được tạo
    column_default_sort = ('created_date', True)
    search_placeholder = "Tìm nhân viên..."

    column_list = (
        'id', 'customer', 'staff',
        'date', 'time', 'notes', 'total_price'
    )

    column_labels = {
        'id': 'Mã đặt hàng',
        'customer': 'Khách hàng',
        'staff': 'Nhân viên',
        'date': 'Ngày đặt',
        'time': 'Giờ đặt',
        'notes': 'Ghi chú',
        'total_price': 'Tạm tính'
    }

    def get_query(self):
        query = super().get_query()
        #Nếu url ko có flt0_0 thì sẽ lấy booking trong ngày
        if request.args.get('flt0_0'):
            filterDate = datetime.strptime(request.args.get('flt0_0'), '%Y-%m-%d').date()
            query = query.filter(Booking.date == filterDate)
        return query

    def get_count_query(self):
        query = super().get_count_query()
        if request.args.get('flt0_0'):
            filterDate = datetime.strptime(request.args.get('flt0_0'), '%Y-%m-%d').date()
            query = query.filter(Booking.date == filterDate)
        return query

    def search_placeholder(self):
        return "Tìm nhân viên..."

def init_receptionist(app):
    receptionist_index = MyReceptionistIndexView(url="/receptionist/", endpoint="receptionist_index", name="Thông tin")
    receptionist = Admin(
        app,
        name="Beauty Spa - Receptionist",
        theme=Bootstrap4Theme(),
        endpoint="receptionist_index",
        index_view=receptionist_index,
        url="/receptionist"
    )
    receptionist.add_view(MyServiceView(Service, db.session, name='Dịch vụ', endpoint='service_receptionist'))
    receptionist.add_view(MyBookingView(Booking, db.session, name='Lịch đã đặt', endpoint='booking_receptionist'))
    receptionist.add_view(MyEmployeeWorkScheduleView(Booking, db.session, 'Lịch làm việc', endpoint='employeeSchedule_receptionist'))
    receptionist.add_view(base.BaseLogoutView("Đăng xuất", endpoint="receptionise_logout"))