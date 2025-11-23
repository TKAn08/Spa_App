from datetime import datetime
from flask import render_template, request, flash, redirect, url_for, session, Blueprint
from flask_login import current_user, login_user, logout_user
from spa_app.models import User, UserRole
from spa_app.dao import user_dao
from spa_app import app, login, admin_bp, admin

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect("/")
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        currentUser = user_dao.auth_user(username, password)
        print(currentUser)
        if (currentUser):
            login_user(currentUser)
            return redirect("/")
        else:
            error_message = "Tài khoản hoặc mật khẩu không đúng!"
    return render_template('login.html', error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
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

        new_user = User(
            username=username,
            gender=gender,
            DOB=DOB,
            address=address,
            phone_number=phoneNumber,
            first_name=firstName,
            last_name=lastName
        )
        new_user.set_hash_password(password)

        if (user_dao.add_user(new_user)):
            flash("Đăng ký thành công", "success")
            return redirect("/login")
        else:
            return redirect("/register")

    return render_template('register.html')

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/login")

@login.user_loader
def load_user(user_id):
    return user_dao.get_user_by_id(user_id)

@admin_bp.route("/admin-login", endpoint="admin-login", methods=['GET', 'POST'])
def admin_login_view():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect("/admin")
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_dao.auth_user(username, password)
        if user and user.role == UserRole.ADMIN:
            login_user(user)
            return redirect("/admin")
        else:
            error_message = "Tài khoản không hợp lệ!"
    return render_template("admin/admin-login.html", error_message=error_message)

app.register_blueprint(admin_bp)

if __name__ == '__main__':
    with app.app_context():
        print(app.url_map)
        app.run(host="127.0.0.1", port=5001, debug=True)