from functools import wraps
from flask import abort
from flask_login import current_user

from spa_app.models import UserRole


def user_only_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        # Không phải USER
        try:
            if current_user.role != UserRole.USER:
                raise Exception()
            return f(*args, **kwargs)
        except:
            abort(403)

    return decorated_func