from spa_app.admin_route import base
from flask_admin import Admin, expose

from spa_app.admin_route.base import BaseLogoutView
from spa_app.models import UserRole, User, Service, Category
from wtforms.fields.simple import TextAreaField, PasswordField
from wtforms.widgets import TextArea
from spa_app import db
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
    column_list = ['name', 'products']
    column_searchable_list = ['name']
    column_filters = ['name']

class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

def init_admin(app):
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
    admin.add_view(MyUserView(User, db.session))
    admin.add_view(MyCategoryView(Category, db.session))
    admin.add_view(MyServiceView(Service, db.session, name='Dịch vụ', endpoint='service_admin'))
    admin.add_view(BaseLogoutView("Đăng xuất", endpoint="admin_logout"))