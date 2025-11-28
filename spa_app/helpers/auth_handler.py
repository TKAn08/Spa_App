from flask import request, render_template
from flask_login import current_user, login_user, logout_user
from werkzeug.utils import redirect
from spa_app.dao import user_dao
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask import redirect
from flask_admin.theme import Bootstrap4Theme
from spa_app.models import UserRole

def handler_login_view(required_role, redirect_url, template_name):
    if current_user.is_authenticated and current_user.role == required_role:
        return redirect(redirect_url)

    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_dao.auth_user(username, password)
        if user and user.role == required_role:
            login_user(user)
            return redirect(redirect_url)
        else:
            error_message = "Tài khoản không hợp lệ!"
    return render_template(template_name, error_message=error_message)



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



def init_view(app):
    admin = Admin(
        app,
        name="Beauty Spa",
        theme=Bootstrap4Theme(),
        index_view=MyAdminIndexView()
    )
    # admin.add_view(AuthenticatedView(User, db.session))
    admin.add_view(MyLogoutView("Đăng xuất"))