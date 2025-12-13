from spa_app import db
from spa_app.models import User
from datetime import date, datetime
#file này chứa giao diện người dùng

def add_user(user: User):
    try:
        db.session.add(user)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    checkingUser = User.query.filter(User.username==username).first()
    if (checkingUser and checkingUser.check_password(password)):
        return checkingUser
    return None

def get_age_user(dob):
    if dob is None:
        return None
    if (isinstance(dob, datetime)):
        dob = dob.date()
    today = date.today()
    return (
        today.year - dob.year -
        ((today.month, today.day) < (dob.month, dob.day))
    )

def change_password(user, new_password):
    user.set_hash_password(new_password)
    db.session.commit()

def check_invalid_phone_number(phone_number):
    return User.query.filter(User.phone_number==phone_number).first() is not None

def change_information(user, name, gender, dob, address, phone_number):
    user.name = name
    user.gender = gender
    user.DOB = dob
    user.address = address
    user.phone_number = phone_number
    db.session.commit()
