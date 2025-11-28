from flask import Blueprint
from spa_app.helpers.auth_handler import handler_login_view
from spa_app.models import UserRole

# file này chứa các route thuộc admin

admin_bp = Blueprint('admin_bp', __name__)
cashier_bp = Blueprint('cashier_bp', __name__)

@admin_bp.route("/admin-login", methods=['GET', 'POST'])
def admin_login_view():
    return handler_login_view(UserRole.ADMIN, "/admin", "admin/admin-login.html")

@cashier_bp.route("/admin-login", methods=['GET', 'POST'])
def cashier_login_view():
    return handler_login_view(UserRole.CASHIER, "/cashier", "admin/admin-login.html")