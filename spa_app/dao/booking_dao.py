from datetime import date, timedelta, datetime, time
from spa_app.models import Booking, BookingStatus, PaymentStatus, db, Employee, User
from sqlalchemy import func
today = date.today()
#Lấy ngày đầu tuần này
start_of_month = today.replace(day=1)
#Lấy ngày cuối tuần này
next_month = (start_of_month + timedelta(days=32)).replace(day=1)

def datetime_range(start_date, end_date):
    start = datetime.combine(start_date, time.min)
    end = datetime.combine(end_date, time.min)
    return start, end

def count_bookings_in_month():
    start, end = datetime_range(start_of_month, next_month)
    return get_count_booking_by_time(start, end)

def count_bookings_in_day():
    tomorrow = datetime.today() + timedelta(days=1)
    start, end = datetime_range(today, tomorrow)
    return get_count_booking_by_time(start, end)

def get_count_booking_by_time(start, end):
    return Booking.query.filter(
        Booking.created_date >= start,
        Booking.created_date <= end
    ).count()

#Tính tổng doanh thu tháng
def get_revenue_in_month():
    start, end = datetime_range(start_of_month, next_month)
    return get_revenue_by_time(start, end)

#Tính tổng doanh thu ngày
def get_revenue_in_day():
    tomorrow = datetime.today() + timedelta(days=1)
    start, end = datetime_range(today, tomorrow)
    return get_revenue_by_time(start, end)


#Truy vấn tổng doanh thu theo thời gian(Hàm chung)
def get_revenue_by_time(start, end):
    return db.session.query(
        func.sum(Booking.total_price)
    ).filter(
        Booking.created_date >= start,
        Booking.created_date < end,
        Booking.status == BookingStatus.COMPLETED,
        Booking.payment == PaymentStatus.PAID
    ).scalar() or 0

def get_revenue_each_day_in_week():
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=7)
    return db.session.query(
        func.date(Booking.created_date),
        func.sum(Booking.total_price)
    ).filter(
        Booking.created_date >= start,
        Booking.created_date < end,
        Booking.status == BookingStatus.COMPLETED,
        Booking.payment == PaymentStatus.PAID
    ).group_by(
        func.date(Booking.created_date)
    ).order_by(
        func.date(Booking.created_date)
    ).all()

def get_current_count_customer():
    #SELECT count(distinct(b.customer_id)) FROM Booking b
    #WHERE b.status == BookingStatus.CONFIRM
    return db.session.query(
        func.count(func.distinct(Booking.customer_id))
    ).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).scalar() or 0

def get_current_count_employee():
    #SELECT count(e.id) FROM Employee e
    #WHERE e.status == 'Đang làm' AND e.active == TRUE
    return (db.session.query(
        func.count(Employee.id)
    ).join(User, User.id == Employee.id)
    .filter(
        Employee.status == 'Đang làm',
        User.active == True
    ).scalar() or 0)