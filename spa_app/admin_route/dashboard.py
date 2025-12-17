def init_view(app):
    from spa_app.admin_route.roles import cashier, admin, employee,receptionist
    admin.init_admin(app)
    cashier.init_cashier(app)
    employee.init_employee(app)
    receptionist.init_receptionist(app)




