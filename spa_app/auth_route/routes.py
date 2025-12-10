from datetime import datetime
from spa_app.models import User
from flask import render_template, request, redirect, flash, Blueprint, session
from flask_login import current_user, login_user, logout_user
from spa_app.dao import user_dao
from spa_app.auth_route.auth_handler import handler_login_view

# file này chứa các route đăng nhập, đăng ký của người dùng
main_auth_bp = Blueprint('auth_bp', __name__)
admin_bp = Blueprint('admin_bp', __name__)

@main_auth_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect("/")
    next_url = request.args.get('next')
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        currentUser = user_dao.auth_user(username, password)
        if (currentUser):
            login_user(currentUser)
            return redirect(next_url or "/")
        else:
            error_message = "Tài khoản hoặc mật khẩu không đúng!"
    return render_template('login.html', error_message=error_message, next_url=next_url)

@main_auth_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':

        session["reg_data"] = request.form.to_dict()

        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm_password')
        gender = request.form.get('gender') or None
        DOB_str = request.form.get('dob') or None
        address = request.form.get('address') or None
        phoneNumber = request.form.get('phone_number')
        firstName = request.form.get('first_name')
        lastName = request.form.get('last_name')

        existing_username = User.query.filter_by(username=username).first()
        existing_phone_number = User.query.filter_by(phone_number=phoneNumber).first()

        message = None
        #Kiểm tra username đã tồn tại chưa
        if existing_username:
            flash("Tài khoản đã tồn tại !", "danger")
            return redirect("/register")

        if existing_phone_number:
            flash("Số điện thoại đã được đăng ký !", "danger")
            return redirect("/register")

        DOB = datetime.strptime(DOB_str, "%Y-%m-%d") if DOB_str else None
        name = firstName + " " + lastName

        new_user = User(
            username=username,
            gender=gender,
            DOB=DOB,
            address=address,
            phone_number=phoneNumber,
            name = name
        )
        new_user.set_hash_password(password)

        if user_dao.add_user(new_user):
            flash("Đăng ký thành công! Đang chuyển hướng sang trang đăng nhập...", "success")
            return redirect('/register')
        else:
            flash("Đăng ký thất bại, hệ thống đang gặp lỗi !", "danger")
            return redirect('/register')


    saved_data = session.get("reg_data", {})
    return render_template('register.html', saved_data=saved_data)

@main_auth_bp.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/login")

@admin_bp.route("/admin-login", methods=['GET', 'POST'])
def admin_login_view():
    return handler_login_view("admin/admin-login.html")


