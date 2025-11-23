from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = "ADSSAFAMKLMKASFMIO"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:35715982@localhost/spadb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates/admin")

login = LoginManager(app)