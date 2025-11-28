from datetime import datetime

from sqlalchemy.orm import relationship

from spa_app import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float
from flask_login import UserMixin
from enum import Enum as RoleEnum
from werkzeug.security import generate_password_hash, check_password_hash



class UserRole(RoleEnum):
    USER = 1
    ADMIN = 2
    CASHIER = 3
    RECEPTIONIST = 4
    EMPLOYEE = 5


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
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
    role = Column(Enum(UserRole), default=UserRole.USER)
    type = Column(String(50))  # discriminator column cho STI

    admin_code = Column(String(20), nullable=True)
    cashier_code = Column(String(20), nullable=True)
    receptionist_code = Column(String(20), nullable=True)
    employee_code = Column(String(20), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def set_hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Admin(User):
    __mapper_args__ = {'polymorphic_identity': 'admin'}

class Cashier(User):
    __mapper_args__ = {'polymorphic_identity': 'cashier'}

class Receptionist(User):
    __mapper_args__ = {'polymorphic_identity': 'receptionist'}

class Employee(User):
    __mapper_args__ = {'polymorphic_identity': 'employee'}

# Service
class Service(Base):
    __tablename__ = 'service'
    __table_args__ = {'extend_existing': True}
    image = Column(String(255), default='https://www.google.com.vn/url?sa=i&url=http%3A%2F%2Fthcstayson.pgdtpthaibinh.edu.vn%2Ftin-tuc-su-kien%2Ftin-tuc-tu-phong&psig=AOvVaw1RuqyQiOTlnTHTAROeCIfp&ust=1764385343136000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCPC-yt3tk5EDFQAAAAAdAAAAABAL')
    price = Column(Float)
    duration = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    description = Column(db.Text)

class Category(Base):
    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}
    description = Column(db.Text)
    services = relationship('Service', backref='category', lazy=True)



