
from spa_app import db, create_app
from sqlalchemy import func
from spa_app.models import Service, Category, Booking, BookingService, BookingStatus, PaymentStatus
from flask import current_app
from spa_app.dao.booking_dao import datetime_range, start_of_month, next_month

def load_services(search=None, cate_id=None, page=None):
    query = Service.query
    if search:
        query = query.filter(Service.name.contains(search))

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

def get_service_by_id(id):
    return Service.query.get(id)

def load_categories():
    return Category.query.all()

def get_outstanding_services():
    return Service.query.filter(Service.outstanding).all()

def category_stats():
    # Select c.id, c.name, count(s.id)
    # From Category c
    # inner join Service s
    #     on s.category_id = c.id
    # GroupBy(c.id, c.name)
    return (db.session.query(
        Category.id,
        Category.name,
        func.count(Service.id).label('Số lượng')
    ).join(Service, Category.id == Service.category_id, isouter=True)
            .group_by(Category.id, Category.name)).all()

from sqlalchemy import func

def get_top_3_services_in_month():
    start, end = datetime_range(start_of_month, next_month)

    top_services = (
        db.session.query(
            Service.name,
            func.count(func.distinct(Service.id)).label('total_bookings')
        )
        .join(BookingService, Service.id == BookingService.service_id)
        .join(Booking, BookingService.booking_id == Booking.id)
        .filter(
            Booking.created_date >= start,
            Booking.created_date < end,
            Booking.status == BookingStatus.COMPLETED,
            Booking.payment == PaymentStatus.PAID
        )
        .group_by(Service.id, Service.name)
        .order_by(func.count(func.distinct(Service.id)).desc())
        .limit(3)
        .all()
    )

    return top_services
