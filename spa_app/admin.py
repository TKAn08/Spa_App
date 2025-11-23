from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask import redirect
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user
from spa_app import app, db
from spa_app.models import User, UserRole

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            return redirect("/admin-login")
        return super().index()

    print(app.url_map)


admin = Admin(
    app,
    name="Beauty Spa",
    theme=Bootstrap4Theme(),
    index_view=MyAdminIndexView()
)

admin.add_view(AuthenticatedView(User, db.session))
