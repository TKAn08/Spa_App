from flask import Blueprint, render_template
from spa_app.helpers.auth_handler import handler_login_view
from spa_app.models import UserRole

# file này chứa các route thuộc admin

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route("/admin-login", endpoint="admin-login", methods=['GET', 'POST'])
def admin_login_view():
    err_mess = handler_login_view(UserRole.ADMIN, "/admin");
    return render_template("admin/admin-login.html", error_message=err_mess)
