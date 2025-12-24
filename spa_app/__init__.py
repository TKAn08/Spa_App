from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pdfkit
import cloudinary
login = LoginManager()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    #Tạo PDFKIT
    app.config["PDF_KIT"] = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )
    #Thuế VAT 10%
    app.config['VAT_RATE'] = 10
    #Giảm giá tối đa 20%
    app.config['MAX_DISCOUNT_VALUE'] = 20
    #Truy cập MySQL WorkBench
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:35715982@localhost/spadb?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = "ADSSAFAMKLMKASFMIO"
    #Tạo paginate
    app.config["PAGE_SIZE"] = 6

    #Cloudinary
    cloudinary.config(cloud_name='dohaa2d4l',
                      api_key='496167823262371',
                      api_secret='_zC61PZ0FfpMyi7FCGWl6vFLOOM')
    db.init_app(app)
    login.init_app(app)

    # ====== ĐĂNG KÝ CUSTOM FILTERS ======
    from .filters import (
        format_currency,
        format_date,
        format_datetime,
        format_time,
        format_duration,
        format_phone
    )

    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['format_time'] = format_time
    app.jinja_env.filters['format_duration'] = format_duration
    app.jinja_env.filters['format_phone'] = format_phone

    # ====== ĐĂNG KÝ BLUEPRINT ======
    from spa_app.auth_route.routes import main_auth_bp, admin_bp
    from spa_app.main_route.routes import main_bp

    from spa_app.admin_route.dashboard import init_view
    init_view(app)

    app.register_blueprint(main_auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    return app


from spa_app.dao.user_dao import get_user_by_id


@login.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)