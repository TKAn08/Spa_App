from flask import flash

from spa_app import db
from spa_app.models import User

def add_user(user: User):
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi đăng ký: {str(e)}")
        return False

def auth_user(username, password):
    checkingUser = User.query.filter(User.username==username).first()
    if (checkingUser and checkingUser.check_password(password)):
        return checkingUser
    return None

def get_user_by_id(user_id):
    return User.query.get(user_id)