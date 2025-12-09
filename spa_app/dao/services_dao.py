from spa_app import db, create_app
from spa_app.models import Service, Category
from flask import current_app

def load_services(q=None, cate_id=None, page=None):
    query = Service.query
    if q:
        query = query.filter(Service.name.contains(q))

    if cate_id:
        query = query.filter(Service.category_id == cate_id)

    if page:
        size = count_services_per_page()
        start = (int(page)-1)*size
        query = query.slice(start, start+size)

    return query.all()

def count_services(cate_id=None):
    query = Service.query
    if cate_id:
        query = query.filter(Service.category_id == cate_id)
    return query.count()

def count_services_per_page():
    return current_app.config["PAGE_SIZE"]

def load_services_for_main_page():
    return Service.query.limit(3).all()

def load_categories():
    return Category.query.all()
