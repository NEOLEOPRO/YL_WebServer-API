from flask import Flask, url_for, request, render_template, redirect, make_response, abort
from flask import session as flask_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import os

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.users import User

import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init('db/matric.sqlite')

login_manager = LoginManager()
login_manager.init_app(app)

path_to_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegisterForm(FlaskForm):
    login = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    rep_password = PasswordField('Повтор пароля', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    datep = IntegerField('Дата рождения', validators=[DataRequired()])
    monthp = IntegerField('Месяц рождения', validators=[DataRequired()])
    agep = IntegerField('Год рождения', validators=[DataRequired()])
    submit = SubmitField('Готово')


class LoginForm(FlaskForm):
    login = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class MatricForm(FlaskForm):
    datee = IntegerField('Дата рождения', validators=[DataRequired()])
    monthe = IntegerField('Месяц рождения', validators=[DataRequired()])
    agee = IntegerField('Год рождения', validators=[DataRequired()])
    temp = StringField('Характер\n', validators=[DataRequired()])
    power = StringField('Энергия\n', validators=[DataRequired()])
    intr = StringField('Интерес\n', validators=[DataRequired()])
    heal = StringField('Здоровье\n', validators=[DataRequired()])
    logic = StringField('Логика\n', validators=[DataRequired()])
    work = StringField('Труд\n', validators=[DataRequired()])
    luck = StringField('Удача\n', validators=[DataRequired()])
    debt = StringField('Долг\n', validators=[DataRequired()])
    mind = StringField('Память\n', validators=[DataRequired()])
    submit = SubmitField('Рассчитать')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.login.data,
            datep=form.datep.data,
            monthp=form.monthp.data,
            agep=form.agep.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
    

@app.route("/")
def index():
    form = MatricForm()
    return render_template("index.html", title="Нумерология", form=form)


@app.route("/matric")
@login_required
def matric():
    form = MatricForm()
    d = current_user.datep
    m = current_user.monthp
    y = current_user.agep
    a = d // 10 + d % 10 + m // 10 + m % 10 + y % 10 + (y // 10) % 10 + (y // 10) // 10 % 10 + (y // 10) // 10 // 10 % 10
    b = a // 10 + a % 10
    c = a - 2 * (d // 10 + d * (d // 10 == 0))
    e = c // 10 + c % 10
    s = ''.join([str(d), str(m), str(y), str(a), str(b), str(c), str(e)])
    print(s)
    form.temp = s.count('1') * '1'
    form.power = s.count('2') * '2'
    form.intr = s.count('3') * '3'
    form.heal = s.count('4') * '4'
    form.logic = s.count('5') * '5'
    form.work = s.count('6') * '6'
    form.luck = s.count('7') * '7'
    form.debt = s.count('8') * '8'
    form.mind = s.count('9') * '9'
    return render_template("index.html", title="Нумерология", form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1), 
                       max_age=60 * 60 * 24 * 365)
    else:
        res = make_response("Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1', 
                       max_age=60 * 60 * 24 * 365)
    return res


@app.route('/session_test/')
def session_test():
    if 'visits_count' in flask_session:
        flask_session['visits_count'] = flask_session.get('visits_count') + 1
    else:
        flask_session['visits_count'] = 1
    
    return "visit " + str(flask_session['visits_count'])


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')