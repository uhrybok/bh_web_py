from flask import Flask
from main import main

import models.session as session_model

def create_app():
    app = Flask(__name__)

    app.secret_key = "123_надо _использовать_генератор?"

    @app.context_processor
    def inject_login():
        login_menu = "Войти"
        login_url = "/login"

        user = session_model.current_user()

        if user:
            login_menu = f"Выйти ({user["fname"]})"
            login_url = "/logout"

        return {
            "login_menu": login_menu,
            "login_url": login_url,
            "user": user
        } 

    app.register_blueprint(main)

    return app