from flask_login import current_user, login_required

from spa_app import create_app
app = create_app()

@app.route("/whoami")
@login_required  # chỉ cho phép user đã login
def whoami():
    print(current_user.DOB, type(current_user.DOB))

if __name__ == '__main__':
    with app.app_context():
        print(app.url_map)
        app.run(host="127.0.0.1", port=5001, debug=True)