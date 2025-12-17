from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, RadioField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import datetime, date, time
from spa_app.models import Booking, Employee, Setting, db


class BookingStep1Form(FlaskForm):
    name = StringField("Họ và tên", validators=[DataRequired(), Length(max=150)])
    phone_number = StringField("Số điện thoại", validators=[DataRequired(), Length(max=12)])
    email = StringField("Email", validators=[Optional()])
    address = StringField("Địa chỉ", validators=[Optional()])
    submit = SubmitField("Tiếp tục")


class BookingStep2Form(FlaskForm):
    # Thay đổi từ SelectField sang SelectMultipleField để chọn nhiều dịch vụ
    services = SelectMultipleField("Chọn dịch vụ", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Tiếp tục")


class BookingStep3Form(FlaskForm):
    employee = RadioField("Chọn nhân viên", coerce=int, validators=[Optional()])
    submit = SubmitField("Tiếp tục")

    def validate_employee(self, field):
        """Custom validation để kiểm tra nhân viên đã đủ 5 khách chưa"""
        from spa_app.main_route.routes import session

        # Nếu là "Spa chọn" (employee = 0) thì không cần validate
        if field.data == 0:
            return

        # Lấy thông tin ngày từ session
        booking_data = session.get('booking', {})
        if not booking_data.get('date'):
            return  # Chưa chọn ngày, không validate

        try:
            appointment_date = datetime.strptime(booking_data['date'], "%Y-%m-%d").date()
        except:
            return  # Date format không hợp lệ

        # Kiểm tra số lượng booking của nhân viên trong ngày
        setting = Setting.query.first()
        max_customers = setting.max_booking_per_day if setting else 5

        bookings_count = Booking.query.filter_by(
            staff_id=field.data,
            date=appointment_date
        ).count()

        if bookings_count >= max_customers:
            employee = Employee.query.get(field.data)
            raise ValidationError(
                f"Nhân viên {employee.name} đã có {bookings_count}/{max_customers} khách trong ngày này. "
                f"Vui lòng chọn nhân viên khác hoặc để spa chọn."
            )


class BookingStep4Form(FlaskForm):
    appointment_date = SelectField("Chọn ngày", validators=[DataRequired()])
    appointment_time = SelectField("Chọn giờ", validators=[DataRequired()])
    submit = SubmitField("Tiếp tục")

    def validate_appointment_time(self, field):
        """Kiểm tra thời gian không trùng với booking khác"""
        from spa_app.main_route.routes import session

        booking_data = session.get('booking', {})
        employee_id = booking_data.get('employee_id')

        # Nếu không chọn nhân viên cụ thể (spa chọn) thì không cần validate trùng
        if not employee_id or employee_id == 0:
            return

        # Kiểm tra date đã được chọn chưa
        if not self.appointment_date.data:
            return

        try:
            appointment_date = datetime.strptime(self.appointment_date.data, "%Y-%m-%d").date()
            appointment_time = datetime.strptime(field.data, "%H:%M").time()
        except:
            return

        # Kiểm tra xem đã có booking nào trùng nhân viên, ngày, giờ chưa
        existing_booking = Booking.query.filter_by(
            staff_id=employee_id,
            date=appointment_date,
            time=appointment_time
        ).first()

        if existing_booking:
            raise ValidationError(
                f"Thời gian này đã được đặt. Vui lòng chọn giờ khác."
            )


class BookingConfirmForm(FlaskForm):
    notes = TextAreaField("Ghi chú", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Xác nhận đặt lịch")