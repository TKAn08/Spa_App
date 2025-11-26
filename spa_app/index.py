from spa_app import create_app
app = create_app()

# file chạy chính

if __name__ == '__main__':
    with app.app_context():
        print(app.url_map)
        app.run(host="127.0.0.1", port=5001, debug=True)