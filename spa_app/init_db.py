from datetime import datetime
import json

from spa_app import create_app, db
from spa_app.models import (
    User, UserRole, Service, Category,
    Booking, BookingService, Setting
)

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # --- Xóa tất cả bảng cũ ---
        db.drop_all()
        print("🗑️  Xóa bảng cũ xong")

        # --- Tạo lại tất cả bảng ---
        db.create_all()
        print("✅ Tạo bảng mới xong")

        # --- Tạo admin mặc định ---
        admin_user = User(
            name="Nguyễn Văn A",
            username="TKAn0811",
            phone_number="0933919592",
            role=UserRole.ADMIN
        )
        admin_user.set_hash_password("123456")
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Admin '{admin_user.username}' đã được thêm")

        # --- Thêm categories ---
        with open("data/categories.json", encoding="utf-8") as f:
            categories = json.load(f)
            for c in categories:
                db.session.add(Category(**c))

        # --- Thêm services ---
        with open("data/services.json", encoding="utf-8") as b:
            services = json.load(b)
            for s in services:
                db.session.add(Service(**s))

        # --- Thêm users ---
        with open("data/users.json", encoding="utf-8") as f:
            users = json.load(f)
            for u in users:
                u["password"] = User.hash_password(u["password"])
                u["DOB"] = datetime.strptime(u["DOB"], "%Y-%m-%d").date()
                u["role"] = UserRole[u["role"].upper()]
                db.session.add(User(**u))

        db.session.commit()
        print("🎉 Init DB hoàn tất!")
