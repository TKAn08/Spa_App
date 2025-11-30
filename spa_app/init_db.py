from spa_app import create_app, db
from spa_app.models import Admin, UserRole, Service, Category
import json

app = create_app()
if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # with open("data/categories.json", encoding="utf-8") as b:
        #     categories = json.load(b)
        #
        #     for c in categories:
        #         db.session.add(Category(**c))
        with open("data/services.json", encoding="utf-8") as b:
            services = json.load(b)

            for s in services:
                db.session.add(Service(**s))

    #     admin = Admin(
    #         name="Nguyễn Văn A",
    #         username="TKAn0811",
    #         phone_number="0933919592",
    #         role=UserRole.ADMIN
    #     )
    #     admin.set_hash_password("123456")
    #     db.session.add(admin)
    #     db.session.query(Service).delete()
        db.session.commit()




