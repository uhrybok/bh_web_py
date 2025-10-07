from . import main

from functools import wraps
from flask import render_template, redirect, request, url_for

import models.session as session_model
import models.weather as weather
import models.quiz as quiz

def check_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session_model.is_login():
            return f(*args, **kwargs)
        return redirect(url_for('main.login_page'))
    return wrapper 

@main.route("/")
def index():
    return render_template('index.html')

@main.route("/login/", methods=['GET', 'POST'])
def login_page():
    err = ""
    if request.method == "POST":
        res, err = session_model.check_login(request.form)
        if  res:
            return redirect(url_for('main.index'))
    return render_template('login.html', errors = err)

@main.route("/signup/", methods=['GET', 'POST'])
def signup_page():
    err = None
    data = None
    if request.method == "POST":
        res, err = session_model.check_reg(request.form)
        if  res:
            return redirect(url_for('main.index'))
        else:
            data = request.form
    return render_template('signup.html', errors = err, data = data)

@main.route("/logout/")
def logout():
    session_model.logout()
    return redirect(url_for('main.login_page'))

@main.route("/weather/")
@check_login
def weather_page():
    return render_template('weather.html')

@main.route("/weather/<city>")
@check_login
def weather_city(city):
    city_weather = weather.city(city)
    return render_template('city.html', data = city_weather)

@main.route("/grid")
@check_login
def hw5():
    return render_template('grid.html')

@main.route("/quiz/", methods=['GET', 'POST'])
@check_login
def quiz_page():
    mode, data, question = quiz.quiz_logic(request.method, request.form)
    return render_template('quiz.html', mode = mode, data = data, question = question)

# Сработает если ошибка 404 - т.е. любой другой путь который выше не предусмотрен
@main.errorhandler(404)
def page_not_found():
    return render_template('error404.html')
