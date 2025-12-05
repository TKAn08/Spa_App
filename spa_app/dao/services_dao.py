from spa_app import db
from spa_app.models import Service

def load_services(q=None):
    return Service.query.all()

def load_services_for_main_page():
    return Service.query.limit(3).all()
