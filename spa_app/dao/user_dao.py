from spa_app import db
from spa_app.models import User

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

