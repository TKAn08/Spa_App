from spa_app import create_app, db
from spa_app.models import Admin, UserRole

app = create_app()
if __name__ == '__main__':
    with app.app_context():
    #     admin = Admin(
    #         name="Nguyễn Văn A",
    #         username="TKAn0811",
    #         phone_number="0933919592",
    #         role=UserRole.ADMIN
    #     )
    #     admin.set_hash_password("123456")
    #     db.session.add(admin)
    #     db.session.commit()
        db.create_all()


