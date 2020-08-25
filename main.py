import os
from datetime import date as truedate
from flask import Flask, request, render_template, redirect, make_response
from flask import session as flask_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
application = app

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
    datee = IntegerField('', validators=[DataRequired()])
    monthe = IntegerField('', validators=[DataRequired()])
    agee = IntegerField('', validators=[DataRequired()])
    submit = SubmitField('Рассчитать')


class PortraitForm(FlaskForm):
    datee = IntegerField('', validators=[DataRequired()])
    monthe = IntegerField('', validators=[DataRequired()])
    agee = IntegerField('', validators=[DataRequired()])
    submit = SubmitField('Рассчитать')


def getmatric(d, m, y):
    a = sum([int(i) for i in (str(d) + str(m) + str(y))])
    b = sum([int(i) for i in str(a)])
    c = a - 2 * (d // 10 + d * (d // 10 == 0))
    e = c // 10 + c % 10
    s = str(d) + str(m) + str(y) + str(a) + str(b) + str(c) + str(e)
    while b > 9 and b != 11:
        b = sum([int(i) for i in str(b)])
    self = [s.count('1') * '1', s.count('2') * '2', s.count('3') * '3', s.count('4') * '4', s.count('5') * '5', s.count('6') * '6', s.count('7') * '7', s.count('8') * '8', s.count('9') * '9', str(s.count('7') + s.count('5') + s.count('3')), str(s.count('1') + s.count('4') + s.count('7')), str(s.count('2') + s.count('5') + s.count('8')), str(s.count('3') + s.count('6') + s.count('9')), str(s.count('4') + s.count('5') + s.count('6')), str(b)]
    for p in range(len(self)):
        if not self[p]:
            self[p] = 'Пусто'
        self[p] = '[' + self[p] + ']'
    return dict(char=self[0], power=self[1], intr=self[2], heal=self[3], logic=self[4], work=self[5], luck=self[6], debt=self[7], mind=self[8], temp=self[9], purp=self[10], famil=self[11], habit=self[12], mofl=self[13], nofl=self[14])


def getportrait(d, m, y):
    d = d % 22
    y = sum([int(i) for i in str(y)]) % 22
    numb = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V', '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X', '11': 'XI', '12': 'XII', '13': 'XIII', '14': 'XIV', '15': 'XV', '16': 'XVI', '17': 'XVII', '18': 'XVIII', '19': 'XIX', '20': 'XX', '21': 'XXI', '0': 'XXII'}
    p = {'p1': d, 'p2': m, 'p3': y, 'p4': d + m, 'p5': m + y, 'p6': d + 2*m + y, 'p7': d + m + y, 'p8': d + 3*m + y, 'p9': abs(d - m), 'p10': abs(m - y), 'p11': abs(abs(d - m) - abs(m - y)), 'p12': 2*d + 4*m + 2*y, 'p16': 2*d + 2*m + 2*y, 'p21': 3*d + 5*m + 3*y, 'pA': 2*d + m, 'pB': d + 2*m, 'pC': 2*m + y, 'pD': 2*y + m, 'pE': 2*d + 3*m + y, 'pF': d + 3*m + 2*y, 'pH': 4*d + 4*m + y}
    for i in p:
        p[i] = numb[str(p[i] % 22)]
    return p


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form, to='')
    return render_template('login.html', title='Авторизация', form=form, to='')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают", to='')
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть", to='')
        try:
            truedate(form.agep.data, form.monthp.data, form.datep.data)
        except:
            return render_template('register.html', title='Регистрация', form=form, message="Введена некорректная дата", to='')
        user = User(
            email=form.login.data,
            datep=form.datep.data,
            monthp=form.monthp.data,
            agep=form.agep.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, to='')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
    

@app.route("/", methods=['GET', 'POST'])
def index():
    form = MatricForm()
    return render_template("matric.html", title="Расчёт матрицы", matr=None, form=form, titleto='Портрет', to="/portrait")


@app.route("/matriсself", methods=['GET', 'POST'])
def matricself():
    form = MatricForm()
    return render_template("matric.html", title="Расчёт матрицы", form=form, titleto='Портрет', to="/portrait", matr=getmatric(current_user.datep, current_user.monthp, current_user.agep))


@app.route("/matriс", methods=['GET', 'POST'])
def matric():
    form = MatricForm()
    try:
        truedate(form.agee.data, form.monthe.data, form.datee.data)
    except:
        return render_template('matric.html', title='Расчёт матрицы', titleto='Портрет', to="/portrait", form=form, matr=None, message="Пожалуйста, заполните поля правильно.")
    return render_template("matric.html", title="Расчёт матрицы", form=form, titleto='Портрет', to="/portrait", matr=getmatric(form.datee.data, form.monthe.data, form.agee.data))


@app.route("/matriсharacter", methods=['GET', 'POST'])
def matricharacter():
    form = MatricForm()
    return render_template("mcharacter.html", title="Расчёт матрицы", form=form, titleto='Портрет', to="/portrait", matr=getmatric(current_user.datep, current_user.monthp, current_user.agep))


@app.route("/portrait", methods=['GET', 'POST'])
def portrait():
    form = PortraitForm()
    if form.validate_on_submit():
        try:
            truedate(form.agee.data, form.monthe.data, form.datee.data)
        except:
            return render_template('portrait.html', title='Психологический портрет', form=form, titleto='Матрица', to="/", message="Пожалуйста, заполните поля правильно.", portr=None)
        return render_template('portrait.html', title='Психологический портрет', form=form, titleto='Матрица', to="/", portr=getportrait(form.datee.data, form.monthe.data, form.agee.data))
    return render_template('portrait.html', title='Психологический портрет', form=form, titleto='Матрица', to="/", portr=None)


# @app.route("/cookie_test")
# def cookie_test():
#     visits_count = int(request.cookies.get("visits_count", 0))
#     if visits_count:
#         res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
#         res.set_cookie("visits_count", str(visits_count + 1), max_age=60 * 60 * 24 * 365)
#     else:
#         res = make_response("Вы пришли на эту страницу в первый раз за последние 2 года")
#         res.set_cookie("visits_count", '1', max_age=60 * 60 * 24 * 365)
#     return res


@app.route('/session_test/')
def session_test():
    if 'visits_count' in flask_session:
        flask_session['visits_count'] = flask_session.get('visits_count') + 1
    else:
        flask_session['visits_count'] = 1
    
    return "visit " + str(flask_session['visits_count'])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(port=8080, host='127.0.0.1')