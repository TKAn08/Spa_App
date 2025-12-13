from flask import request, render_template, redirect
from flask_login import current_user, login_user, logout_user
from spa_app.dao import user_dao
from spa_app.models import UserRole


def handler_login_view(template_name):
    if current_user.is_authenticated:
        return redirect(f"/{current_user.value}")

    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role')

        user = user_dao.auth_user(username, password)
        if user:
            try:
                selected_role_enum = UserRole(selected_role)
            except ValueError:
                error_message = "Role không hợp lệ!"
            else:
                if user.role == selected_role_enum:
                    login_user(user)
                    return redirect(f'/{user.role.value}')  # redirect theo enum value
                else:
                    error_message = ("Tài khoản, mật khẩu không đúng "
                                     "hoặc tên đăng nhập {{ user.name }} không tồn tại trên trang này!")
        else:
            error_message = "Tài khoản hoặc mật khẩu không đúng"
    return render_template(template_name, error_message=error_message)



