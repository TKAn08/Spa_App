
from spa_app.admin_route import base
from flask_admin import Admin, expose, BaseView

from spa_app.admin_route.base import BaseLogoutView
from spa_app.dao import services_dao
from spa_app.models import UserRole, User, Service, Category, Booking, db
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

class MyBookingView(AuthenticatedView):
    can_export = True


class MyReportView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/reports.html')

def init_admin(app):
    from spa_app.dao import booking_dao
    from spa_app.filters import format_currency, format_date_vietnamese
    @app.context_processor
    def inject_admin_stats():
        booking_in_month = booking_dao.count_bookings_in_month()
        booking_in_day = booking_dao.count_bookings_in_day()
        revenue_in_month = format_currency(booking_dao.get_revenue_in_month())
        revenue_in_day = format_currency(booking_dao.get_revenue_in_day())
        get_current_count_customer = booking_dao.get_current_count_customer()
        get_current_count_employee = booking_dao.get_current_count_employee()
        get_revenue_each_day_in_week = format_date_vietnamese(booking_dao.get_revenue_each_day_in_week())
        get_top_3_services_in_month = services_dao.get_top_3_services_in_month()
        return dict(
            booking_in_month=booking_in_month,
            booking_in_day=booking_in_day,
            revenue_in_month=revenue_in_month,
            revenue_in_day=revenue_in_day,
            get_current_count_customer=get_current_count_customer,
            get_current_count_employee=get_current_count_employee,
            get_revenue_each_day_in_week=get_revenue_each_day_in_week,
            get_top_3_services_in_month=get_top_3_services_in_month
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
    admin.add_view(BaseLogoutView("Đăng xuất", endpoint="admin_logout"))