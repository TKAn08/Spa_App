from flask_login import current_user, login_required
from spa_app.dao import booking_dao
from spa_app import create_app
from spa_app.models import DiscountStatus

app = create_app()

@app.route("/whoami")
@login_required  # chỉ cho phép user đã login
def whoami():
    print(current_user.DOB, type(current_user.DOB))

if __name__ == '__main__':
    with app.app_context():
        data = booking_dao.get_booking_by_id(1)
        app.run(host="127.0.0.1", port=5001, debug=True)