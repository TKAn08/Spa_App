from datetime import datetime

from flask import request, render_template, redirect, session, flash
from flask_login import current_user, login_user, logout_user
from spa_app.dao import user_dao
from spa_app.models import UserRole, User



def handler_login_view(template_name, check_role=False):
    if current_user.is_authenticated:
        return redirect(f"/{current_user.role.value.lower()}" if check_role else "/")

    error_message = None
    saver_username = session.get('saver_username', '')
    next_url = request.args.get('next')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        #Tạo biến session để lưu tên đăng nhập
        session['saver_username'] = username

        user = user_dao.auth_user(username, password)
        if user:
            # Nếu check_role == True đối với admin, cashier, employee, receptionist
            if check_role:
                selected_role = request.form.get('role')
                from spa_app.models import UserRole
                try:
                    selected_role_enum = UserRole(selected_role)
                    if user.role == selected_role_enum:
                        login_user(user)
                        return redirect(f"/{user.role.value.lower()}")
                    else:
                        error_message = ("Tài khoản, mật khẩu không đúng "
                                         "hoặc tên đăng nhập không tồn tại trên trang này!")
                except ValueError:
                    error_message = "Role không hợp lệ!"
            # Nếu check_role == False đối với user thường
            else:
                login_user(user)
                #Trả về next_url hoặc / tùy theo xử lý
                return redirect(next_url or "/")
        else:
            error_message = "Tài khoản hoặc mật khẩu không đúng!"

    return render_template(template_name, error_message=error_message, next_url=next_url, saver_username=saver_username)

def handler_register_view(template_name):
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
    return render_template(template_name, saved_data=saved_data)


def login_user_view():
    return handler_login_view('login.html', check_role=False)


def login_admin_view():
    return handler_login_view('admin/admin-login.html', check_role=True)



