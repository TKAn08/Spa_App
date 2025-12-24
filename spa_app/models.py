from datetime import datetime
from sqlalchemy.orm import relationship
from spa_app import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float, event
from flask_login import UserMixin
from enum import Enum as RoleEnum
from werkzeug.security import generate_password_hash, check_password_hash


# ENUM ROLES

class UserRole(RoleEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    CASHIER = "CASHIER"
    RECEPTIONIST = "RECEPTIONIST"
    EMPLOYEE = "EMPLOYEE"


# BASE MODEL

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.name

    def isActive(self):
        if self.active:
            return "Kích hoạt"
        return None;
# USER

class User(Base, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    gender = Column(String(50))
    DOB = Column(DateTime)
    address = Column(String(150))
    phone_number = Column(String(12), nullable=False)
    avatar = Column(String(255), default='https://cdn-icons-png.flaticon.com/512/847/847969.png')
    role = Column(Enum(UserRole), default=UserRole.USER)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def set_hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return self.name

    @property
    def isEmployee(self):
        emp = Employee.query.filter_by(id=self.id).first()
        return emp.status if emp else None



# ROLE TABLES

class Admin(db.Model):
    __tablename__ = "admin"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    admin_code = Column(String(20), unique=True)
    last_login = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    note = Column(db.Text)
    user = relationship("User", backref="admin", uselist=False)


class Cashier(db.Model):
    __tablename__ = "cashier"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    cashier_code = Column(String(20), unique=True)
    shift = Column(Enum('Ca sáng', 'Ca chiều'))
    salary = Column(Float)
    note = Column(db.Text)
    user = relationship("User", backref="cashier", uselist=False)


class Receptionist(db.Model):
    __tablename__ = "receptionist"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    receptionist_code = Column(String(20), unique=True)
    shift = Column(Enum('Ca sáng', 'Ca chiều'))
    salary = Column(Float)
    note = Column(db.Text)
    user = relationship("User", backref="receptionist", uselist=False)


class Employee(db.Model):
    __tablename__ = "employee"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    employee_code = Column(String(20), unique=True)
    shift = Column(Enum('Ca sáng', 'Ca chiều'))
    salary = Column(Float)
    experience_year = Column(Integer)
    email = Column(String(255), unique=True)
    status = Column(Enum('Đang làm', 'Nghỉ phép', 'Tạm nghỉ'), nullable=False, default='Đang làm')
    note = Column(db.Text)
    user = relationship("User", backref="employee", uselist=False)


# CATEGORY

class Category(Base):
    __tablename__ = 'category'
    description = Column(db.Text)
    services = relationship("Service", back_populates="category", lazy=True)

    def __str__(self):
        return self.name


# SERVICE

class Service(Base):
    __tablename__ = 'service'

    image = Column(String(255), default="https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg")
    price = Column(Float)
    duration = Column(Integer)
    outstanding = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    description = Column(db.Text)
    category = relationship("Category", back_populates="services")

    service_bookings = relationship(
        "BookingService",
        back_populates="service",
        cascade="all, delete-orphan",
        overlaps="bookings"
    )

    bookings = relationship(
        "Booking",
        secondary="booking_service",
        back_populates="services",
        overlaps="service_bookings"
    )


# BOOKING STATUS ENUM

class BookingStatus(RoleEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class PaymentStatus(RoleEnum):
    UNPAID = "UNPAID"
    PAID = "PAID"

class DiscountStatus(RoleEnum):
    NONE = 'NONE'
    DISCOUNT = 'DISCOUNT'
# BOOKING SERVICE (association)

class BookingService(db.Model):
    __tablename__ = 'booking_service'

    booking_id = Column(Integer, ForeignKey('booking.id'), primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'), primary_key=True)
    quantity = Column(Integer, default=1)

    booking = relationship(
        "Booking",
        back_populates="booking_services",
        overlaps="services"
    )

    service = relationship(
        "Service",
        back_populates="service_bookings",
        overlaps="bookings"
    )


# BOOKING

class Booking(db.Model):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now)

    customer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    date = Column(db.Date, nullable=False)
    time = Column(db.Time, nullable=False)

    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    payment = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)
    total_price = Column(Float, default=0)

    customer = relationship("User", foreign_keys=[customer_id])
    staff = relationship("User", foreign_keys=[staff_id])

    #Tỉ lệ giảm
    discount_value = Column(Float, default=0)
    #Số tiền giảm
    discount_amount = Column(Float)
    #Số tiền cuối cùng (Tính cả mã và thuế VAT)
    final_price = Column(Float, default=total_price)
    discount_type = Column(Enum(DiscountStatus), default=DiscountStatus.NONE)
    notes = Column(db.Text)
    booking_services = relationship(
        "BookingService",
        back_populates="booking",
        cascade="all, delete-orphan",
        overlaps="services"
    )

    services = relationship(
        "Service",
        secondary="booking_service",
        back_populates="bookings",
        overlaps="booking_services,service_bookings"
    )



# SETTINGS

class Setting(Base):
    __tablename__ = 'setting'
    max_booking_per_day = Column(Integer, default=5)


# AUTO CREATE ROLE RECORD

@event.listens_for(User, "after_insert")
def create_role_record(mapper, connection, target):
    if target.role == UserRole.ADMIN:
        connection.execute(Admin.__table__.insert().values(id=target.id, admin_code=f"ADM_{target.id:04d}"))
    elif target.role == UserRole.CASHIER:
        connection.execute(Cashier.__table__.insert().values(id=target.id, cashier_code=f"CSH_{target.id:04d}"))
    elif target.role == UserRole.RECEPTIONIST:
        connection.execute(
            Receptionist.__table__.insert().values(id=target.id, receptionist_code=f"REP_{target.id:04d}"))
    elif target.role == UserRole.EMPLOYEE:
        connection.execute(Employee.__table__.insert().values(id=target.id, employee_code=f"EMP_{target.id:04d}"))
