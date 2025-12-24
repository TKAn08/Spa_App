from datetime import datetime
from spa_app.models import User
from flask import render_template, request, redirect, flash, Blueprint, session
from flask_login import current_user, login_user, logout_user
from spa_app.dao import user_dao
from spa_app.auth_route.auth_handler import login_user_view, login_admin_view, handler_register_view

# file này chứa các route đăng nhập, đăng ký của người dùng
main_auth_bp = Blueprint('auth_bp', __name__)
admin_bp = Blueprint('admin_bp', __name__)

@main_auth_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    return login_user_view()

@main_auth_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    return handler_register_view('register.html')

@main_auth_bp.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/login")

@admin_bp.route("/admin-login", methods=['GET', 'POST'])
def admin_login_view():
    return login_admin_view()

