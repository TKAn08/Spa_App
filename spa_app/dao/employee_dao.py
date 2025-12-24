from sqlalchemy.orm import aliased

from spa_app import db
from sqlalchemy import func
from spa_app.models import Employee, Booking, User
from spa_app.dao.booking_dao import start_of_month, next_month, datetime_range

def load_all_employee():
    return Employee.query.all()

def get_top_5_best_employee_in_month():

    start, end = datetime_range(start_of_month, next_month)
    return db.session.query(
        User.id.label('employee_id'),
        User.name.label('employee_name'),
        func.count(Booking.staff_id).label('so_luong_lich_hoan_thanh')
    ).join(
        Booking, Booking.staff_id == User.id
    ).filter(
        Booking.created_date >= start,
        Booking.created_date < end,
    ).group_by(
        User.id, User.name
    ).order_by(
        func.count(Booking.staff_id).desc()
    ).limit(5).all()

# def getEmployeeSchedule(staff_id):
#     #Tạo 2 bảng sao của User
#     Employee = aliased(User)
#     Customer = aliased(User)
#     return db.session.query(
#         Booking.id,
#         Employee.name.label('staff_name'),
#         Customer.name.label('customer_name'),
#         Booking.date,
#         Booking.time,
#         Booking.notes,
#         Booking.total_price
#     ).join(Employee, Booking.staff_id == Employee.id)\
#      .join(Customer, Booking.customer_id == Customer.id)\
#      .filter(Booking.staff_id == staff_id)\
#      .all()