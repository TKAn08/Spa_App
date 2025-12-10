from datetime import datetime

from sqlalchemy.orm import relationship

from spa_app import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float, event
from flask_login import UserMixin
from enum import Enum as RoleEnum
from werkzeug.security import generate_password_hash, check_password_hash



class UserRole(RoleEnum):
    USER = "user"
    ADMIN = "admin"
    CASHIER = "cashier"
    RECEPTIONIST = "receptionist"
    EMPLOYEE = "employee"


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)

# User
class User(Base, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    gender = Column(String(50))
    DOB = Column(DateTime)
    address = Column(String(150))
    phone_number = Column(String(12), nullable=False)
    image = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def set_hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
    shift =  Column(Enum('Ca sáng', 'Ca chiều'))
    salary = Column(Float)
    experience_year = Column(Integer)
    email = Column(String(255), unique=True)
    status = Column(Enum('Đang làm', 'Nghỉ phép', 'Tạm nghỉ'))
    note = Column(db.Text)

    user = relationship("User", backref="employee", uselist=False)


# Service
class Service(Base):
    __tablename__ = 'service'
    __table_args__ = {'extend_existing': True}
    image = Column(String(255), default='https://www.google.com.vn/url?sa=i&url=http%3A%2F%2Fthcstayson.pgdtpthaibinh.edu.vn%2Ftin-tuc-su-kien%2Ftin-tuc-tu-phong&psig=AOvVaw1RuqyQiOTlnTHTAROeCIfp&ust=1764385343136000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCPC-yt3tk5EDFQAAAAAdAAAAABAL')
    price = Column(Float)
    duration = Column(Integer)
    outstanding = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    description = Column(db.Text)

class Category(Base):
    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}
    description = Column(db.Text)
    services = relationship('Service', backref='category', lazy=True)


@event.listens_for(User, "after_insert")
def create_role_record(mapper, connection, target):
    if target.role == UserRole.ADMIN:
        connection.execute(
            Admin.__table__.insert().values(
                id=target.id,
                admin_code=f"ADM_{target.id:04d}"
            )
        )

    elif target.role == UserRole.CASHIER:
        connection.execute(
            Cashier.__table__.insert().values(
                id=target.id,
                cashier_code=f"CSH_{target.id:04d}"
            )
        )

    elif target.role == UserRole.RECEPTIONIST:
        connection.execute(
            Receptionist.__table__.insert().values(
                id=target.id,
                receptionist_code=f"REP_{target.id:04d}"
            )
        )

    elif target.role == UserRole.EMPLOYEE:
        connection.execute(
            Employee.__table__.insert().values(
                id=target.id,
                employee_code=f"EMP_{target.id:04d}"
            )
        )



