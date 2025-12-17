# spa_app/helpers/booking_helpers.py
from datetime import datetime, timedelta
from spa_app.models import Booking, BookingStatus, Setting, Employee, User

def is_booking_valid(staff_id, appointment_date, appointment_time, service_durations):
    """
    Kiểm tra booking hợp lệ:
    - Giới hạn max khách/ngày
    - Trùng thời gian (bao gồm tổng thời lượng dịch vụ)
    """
    start_time = datetime.combine(appointment_date, appointment_time)
    total_duration = sum(service_durations)  # phút
    end_time = start_time + timedelta(minutes=total_duration)

    # max khách/ngày
    setting = Setting.query.first()
    max_bookings = setting.max_booking_per_day if setting else 5

    bookings_count = Booking.query.filter(
        Booking.staff_id == staff_id,
        Booking.date == appointment_date,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
    ).count()

    if bookings_count >= max_bookings:
        return False, f"Nhân viên đã đầy lịch ({bookings_count}/{max_bookings} khách)."

    # Kiểm tra trùng giờ
    existing_bookings = Booking.query.filter(
        Booking.staff_id == staff_id,
        Booking.date == appointment_date,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
    ).all()

    for b in existing_bookings:
        b_start = datetime.combine(b.date, b.time)
        b_end = b_start + timedelta(minutes=sum(s.duration for s in b.services))
        if not (end_time <= b_start or start_time >= b_end):
            return False, f"Thời gian từ {start_time.time()} đến {end_time.time()} trùng với booking khác."

    return True, "Booking hợp lệ"


def auto_assign_employee(appointment_date, appointment_time, service_durations):
    """
    Nếu user chọn nhân viên = 0, tự động chọn nhân viên trống
    """
    employees = Employee.query.join(User).filter(
        Employee.status == 'Đang làm',
        User.active == True
    ).all()

    for emp in employees:
        valid, _ = is_booking_valid(emp.id, appointment_date, appointment_time, service_durations)
        if valid:
            return emp.id
    return None
