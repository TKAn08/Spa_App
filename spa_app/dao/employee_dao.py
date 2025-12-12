from spa_app import db
from spa_app.models import Employee

def load_all_employee():
    return Employee.query.all()
