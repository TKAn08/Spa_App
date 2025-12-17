from datetime import datetime, timedelta
from spa_app.models import Booking, BookingStatus, Setting, Employee, User


# =====================================================
# CHECK BOOKING HỢP LỆ
# =====================================================
def is_booking_valid(staff_id, appointment_date, appointment_time, service_durations):
    """
    Kiểm tra booking hợp lệ:
    - staff_id hợp lệ
    - nhân viên đang làm
    - trong ca làm việc
    - không vượt max khách/ngày
    - không vượt tổng giờ làm/ngày
    - không trùng giờ (interval)
    """

    # -------------------------------------------------
    # 1. CHECK NHÂN VIÊN
    # -------------------------------------------------
    if not staff_id:
        return False, "Chưa xác định nhân viên"

    employee = Employee.query.get(staff_id)
    if not employee or employee.status != 'Đang làm':
        return False, "Nhân viên không khả dụng"

    # -------------------------------------------------
    # 2. TÍNH THỜI GIAN BOOKING
    # -------------------------------------------------
    start_time = datetime.combine(appointment_date, appointment_time)
    total_duration = sum(service_durations)  # phút
    end_time = start_time + timedelta(minutes=total_duration)

    # -------------------------------------------------
    # 3. CHECK CA LÀM VIỆC
    # -------------------------------------------------
    SHIFT_TIME = {
        "Ca sáng": (8, 12),
        "Ca chiều": (13, 18)
    }

    if employee.shift in SHIFT_TIME:
        shift_start, shift_end = SHIFT_TIME[employee.shift]

        if start_time.hour < shift_start or end_time.hour > shift_end:
            return False, "Thời gian đặt ngoài ca làm việc của nhân viên"

    # -------------------------------------------------
    # 4. LẤY BOOKING HIỆN TẠI TRONG NGÀY
    # -------------------------------------------------
    existing_bookings = Booking.query.filter(
        Booking.staff_id == staff_id,
        Booking.date == appointment_date,
        Booking.status.in_([
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED
        ])
    ).all()

    # -------------------------------------------------
    # 5. CHECK MAX BOOKING / NGÀY
    # -------------------------------------------------
    setting = Setting.query.first()
    max_bookings = setting.max_booking_per_day if setting else 5

    if len(existing_bookings) >= max_bookings:
        return False, f"Nhân viên đã đủ {max_bookings} khách trong ngày"

    # -------------------------------------------------
    # 6. CHECK TỔNG GIỜ LÀM / NGÀY (8 TIẾNG)
    # -------------------------------------------------
    total_work_minutes = 0
    for b in existing_bookings:
        total_work_minutes += sum(s.duration for s in b.services)

    if total_work_minutes + total_duration > 8 * 60:
        return False, "Nhân viên đã đủ thời gian làm việc trong ngày"

    # -------------------------------------------------
    # 7. CHECK TRÙNG GIỜ (INTERVAL CHECK)
    # -------------------------------------------------
    for b in existing_bookings:
        b_start = datetime.combine(b.date, b.time)
        b_end = b_start + timedelta(
            minutes=sum(s.duration for s in b.services)
        )

        # Trùng khi 2 khoảng giao nhau
        if start_time < b_end and end_time > b_start:
            return (
                False,
                f"Khung giờ {start_time.time()} - {end_time.time()} "
                f"bị trùng với lịch {b_start.time()} - {b_end.time()}"
            )

    # -------------------------------------------------
    return True, "Booking hợp lệ"


# =====================================================
# AUTO ASSIGN NHÂN VIÊN
# =====================================================
def auto_assign_employee(appointment_date, appointment_time, service_durations):
    """
    Tự động chọn nhân viên trống nếu khách không chọn
    """

    employees = Employee.query.join(User).filter(
        Employee.status == 'Đang làm',
        User.active.is_(True)
    ).all()

    for emp in employees:
        valid, _ = is_booking_valid(
            emp.id,
            appointment_date,
            appointment_time,
            service_durations
        )
        if valid:
            return emp.id

    return None
