from flask import request
from flask_login import current_user, login_user
from werkzeug.utils import redirect
from spa_app.dao import user_dao


def handler_login_view(required_role, redirect_url):
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
    return error_message