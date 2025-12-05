from spa_app import create_app, db
from spa_app.models import Admin, UserRole, Service, Category, User
import json

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
    with open("data/services.json", encoding="utf-8") as b:
        services = json.load(b)

        for s in services:
            db.session.add(Service(**s))
        user = User(
            name="Nguyễn Văn B",
            username="user",
            phone_number="0123456789",
        )
        user.set_hash_password('123456')
        db.session.add(user)
        db.session.commit()
        # db.create_all()




