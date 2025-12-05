from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from spa_app.admin_route.roles.admin import Admin
from spa_app.models import UserRole, Service
from spa_app.models import db

class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.CASHIER

class MyCashierIndexView(base.BaseIndexView):
    required_role = UserRole.CASHIER

class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_edit = False  # chỉ chỉnh sửa thông tin cá nhân
    can_delete = False
    can_export = True

def init_cashier(app):
    cashier_index = MyCashierIndexView(url="/cashier/", endpoint="cashier_index", name="Thông tin")
    cashier = Admin(
        app,
        name="Beauty Spa - Cashier",
        theme=Bootstrap4Theme(),
        endpoint="cashier_index",
        index_view=cashier_index,
        url="/cashier"
    )
    cashier.add_view(MyServiceView(Service, db.session, name='Dịch vụ', endpoint='service_cashier'))
    cashier.add_view(base.BaseLogoutView("Đăng xuất", endpoint="cashier_logout"))
