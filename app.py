import os
from flask import Flask
from main import main

import models.session as session_model
from models.quiz import db, db_add_test_data

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.secret_key = "123_надо _использовать_генератор?"

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'db_quiz.db')}"

    db.init_app(app)
    with app.app_context():
        db_add_test_data()

    @app.context_processor
    def inject_login():
        log_in_out_url = "main.login_page"
        log_in_out_menu = "Войти"

        user = session_model.current_user()

        if user:
            log_in_out_url = "main.logout"
            log_in_out_menu = f"Выйти ({user['fname']})"

        return {
            "log_in_out_url": log_in_out_url,
            "log_in_out_menu": log_in_out_menu,
            "user": user
        } 

    app.register_blueprint(main)

    return app