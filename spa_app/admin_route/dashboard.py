from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask import redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user
from spa_app.models import UserRole, User, Service
from spa_app import db
from wtforms import TextAreaField
from wtforms.widgets import TextArea

class AuthenticatedView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            return redirect("/admin-login")
        return super().index()


class MyLogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin-login")

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class MyServiceView(AuthenticatedView):
    column_list = ('name', 'image', 'price', 'category', 'description')
    can_export = True;
    extra_js =  ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'description': CKTextAreaField
    }


def init_view(app):
    # ----------------- ADMIN PANEL -----------------
    admin_index = MyAdminIndexView(url="/admin/", endpoint="admin_index")
    admin = Admin(
        app,
        name="Beauty Spa - Admin",
        theme=Bootstrap4Theme(),
        endpoint="admin_index",
        index_view=admin_index,
        url="/admin"
    )
    admin.add_view(MyServiceView(Service, db.session))
    admin.add_view(AuthenticatedView(User, db.session))
    admin.add_view(MyLogoutView("Đăng xuất", endpoint="admin_logout"))

    # ----------------- CASHIER PANEL -----------------
    cashier_index = MyAdminIndexView(url="/cashier/", endpoint="cashier_index")
    cashier = Admin(
        app,
        name="Beauty Spa - Cashier",
        theme=Bootstrap4Theme(),
        index_view=cashier_index,
        endpoint="cashier-panel",
        url="/cashier"
    )
    cashier.add_view(MyLogoutView("Đăng xuất", endpoint="cashier_logout"))
