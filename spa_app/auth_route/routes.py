from datetime import datetime
from spa_app.models import User
from flask import render_template, request, redirect, flash, Blueprint
from flask_login import current_user, login_user, logout_user
from spa_app.dao import user_dao

# file này chứa các route đăng nhập, đăng ký của người dùng
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect("/")
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        currentUser = user_dao.auth_user(username, password)
        if (currentUser):
            login_user(currentUser)
            return redirect("/")
        else:
            error_message = "Tài khoản hoặc mật khẩu không đúng!"
    return render_template('login.html', error_message=error_message)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
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

        #Kiểm tra username đã tồn tại chưa
        if (existing_username):
            flash("Tên đăng nhập đã tồn tại", "warning")
            return redirect("/register")

        #Kiểm tra số điện thoại đã tồn tại chưa
        if (existing_phone_number):
            flash("Số điện thoại đã được đăng ký", "warning")
            return redirect("/register")

        # Kiểm tra password
        if (password != confirmPassword):
            flash("Mật khẩu không khớp", "error")
            return redirect("/register")

        DOB = None
        if (DOB_str):
            DOB = datetime.strptime(DOB_str, "%Y-%m-%d")
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

        if (user_dao.add_user(new_user)):
            flash("Đăng ký thành công", "success")
            return redirect("/login")
        else:
            return redirect("/register")

    return render_template('register.html')

@auth_bp.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/login")

