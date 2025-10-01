from . import main

from flask import render_template, redirect, request, url_for

import models.weather as weather
import models.session as session_model


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
def sigup_page():
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
def weather_page():
    if session_model.is_login():
        return render_template('weather.html')
    return redirect(url_for('main.login_page'))

@main.route("/weather/<city>")
def weather_city(city):
    if session_model.is_login():
        city_weather = weather.city(city)
        return render_template('city.html', data = city_weather)
    return redirect(url_for('main.login_page'))

@main.route("/grid")
def hw5():
    return render_template('grid.html')

# Сработает если ошибка 404 - т.е. любой другой путь который выше не предусмотрен
@main.errorhandler(404)
def page_not_found():
    return render_template('error404.html')
