from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_PATH = os.path.join(BASE_DIR, "..", "users.json")

def set_session(user):
    session["logged_in"] = True
    session["username"] = user["login"]

def load_users():
    with open(USERS_PATH, "r", encoding="utf-8") as j:
        try:
            users = json.load(j)
        except:
            users = []
    return users

def check_login(form):
    res = False
    err = None

    users = load_users()
    user = next((u for u in users if u["login"] == form["login"]), None)

    if user:
        if check_password_hash(user["password"], form["password"]):
            set_session(user)
            res = True
        else:    
            err = "Неверный пароль или имя пользователя"
    else:
        err = "Неверное имя пользователя или пароль"

    return res, err

def add_user(immu_form):
    res = False

    form = immu_form.to_dict()

    users = load_users()
    
    if any(entry["login"] == form["login"] for entry in users):
        res = False
    else:
        form["password"] = generate_password_hash(form["password"])
        users.append(form)    
        with open(USERS_PATH, "w", encoding="utf-8") as j:
            json.dump(users, j, ensure_ascii=False, indent=4)
            res = True

    return res

def check_reg(form):
    res = True

    field_names = {
        "fname": "Имя",
        "lname": "Фамилия",
        "email": "Имейл",
        "age": "Возраст",
        "login": "Логин",
        "password": "Пароль"
    }
    
    err = {
        key: field_names[key] 
        for key, value in form.items() 
        if not value and key in field_names
    }

    if err:
        res = False
    elif not add_user(form):
        res = False
        err = { "login": "taken" }
    else:    
        set_session(form)

    return res, err

def logout():
    session['logged_in'] = False
    
def is_login():
    if 'logged_in' in session: 
        return session.get('logged_in')
    return False

def current_user():
    if is_login():
        users = load_users()
        return next((u for u in users if u["login"] == session["username"]), None)