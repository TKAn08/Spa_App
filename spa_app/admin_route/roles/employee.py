from spa_app.admin_route import base
from flask_admin.theme import Bootstrap4Theme
from spa_app.admin_route.roles.admin import Admin
from spa_app.models import UserRole


class AuthenticatedView(base.BaseAuthenticatedView):
    required_role = UserRole.CASHIER

class MyEmployeeIndexView(base.BaseIndexView):
    required_role = UserRole.CASHIER

class MyServiceView(AuthenticatedView, base.BaseServiceView):
    can_create = False
    can_edit = False  # chỉ chỉnh sửa thông tin cá nhân
    can_delete = False
    can_export = True

def init_employee(app):
    employee_index = MyEmployeeIndexView(url="/employee/", endpoint="employee_index", name="Thông tin")
    cashier = Admin(
        app,
        name="Beauty Spa - Cashier",
        theme=Bootstrap4Theme(),
        endpoint="employee_index",
        index_view=employee_index,
        url="/employee"
    )
    cashier.add_view(base.BaseLogoutView("Đăng xuất", endpoint="employee_logout"))
