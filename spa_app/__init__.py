from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

login = LoginManager()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)


    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:35715982@localhost/spadb?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = "ADSSAFAMKLMKASFMIO"

    db.init_app(app)
    login.init_app(app)

    # Đăng ký blueprint để dễ quản lý
    from spa_app.auth_route.routes import auth_bp
    from spa_app.admin_route.routes import admin_bp, cashier_bp
    from spa_app.main_route.routes import main_bp

    from spa_app.admin_route.dashboard import init_view
    init_view(app)


    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(cashier_bp)

    return app

from spa_app.dao.user_dao import get_user_by_id
@login.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)