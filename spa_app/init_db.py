from datetime import datetime

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
        # with open("data/users.json", encoding="utf-8") as f:
        #     users = json.load(f)
        #     for u in users:
        #         u["password"] = User.hash_password(u["password"])
        #         u["DOB"] = datetime.strptime(u["DOB"], "%Y-%m-%d").date()
        #         u["role"] = UserRole[u["role"].upper()]
        #         db.session.add(User(**u))

        with open("data/categories.json", encoding="utf-8") as f:
                categories = json.load(f)
                for c in categories:
                    db.session.add(Category(**c))
            # user.set_hash_password('123456')
        # db.session.add(user)
        db.session.commit()
        db.create_all()




