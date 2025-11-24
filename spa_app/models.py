from datetime import datetime
from spa_app import db, app
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
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
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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


# class Service(Base):
#     __tablename__ = 'service'


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # user = User(
        #     first_name="An",
        #     last_name="Trần Khánh",
        #     username="bivatai123",
        #     password="35715982"
        # )
        # db.session.add(user)
        # db.session.commit()
