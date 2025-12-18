from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
class BaseAuthenticatedView(ModelView):
    required_role = None
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.role == self.required_role

    def inaccessible_callback(self, name, **kwargs):
        # Chỉ redirect nếu chưa login
        if not current_user.is_authenticated:
            return redirect(url_for('admin-login'))  # login chung
        # Nếu login nhưng role không đúng, có thể trả 403 thay vì redirect
        from flask import abort
        return abort(403)

class BaseIndexView(AdminIndexView):
    required_role = None
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect("/admin-login")
        if current_user.role != self.required_role:
            from flask import abort
            return abort(403)

        from spa_app.dao import user_dao, services_dao
        user = user_dao.get_user_by_id(current_user.id)
        age = user_dao.get_age_user(user.DOB)
        stats = services_dao.category_stats()

        return self.render('admin/information.html', age=age, user=user, stats=stats)

    @property
    def menu_title(self):
        return "Thông tin"


class BaseLogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin-login")

    def is_accessible(self):
        return current_user.is_authenticated

class BaseServiceView(ModelView):
    column_list = ('name', 'image', 'price', 'category', 'description')
    column_searchable_list = ['name']
    column_filters = ['name']
    column_labels = {
        'name': "Tên Dịch vụ",
        'image': "Hình ảnh",
        'price': "Giá",
        'category': "Loại",
        'description': "Mô tả"
    }
