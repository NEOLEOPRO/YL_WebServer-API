from flask import Flask, url_for, request, render_template, redirect, make_response, abort
from flask import session as flask_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.department import Department
from data.category import Category
import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init('db/mars.sqlite')

login_manager = LoginManager()
login_manager.init_app(app)

path_to_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegisterForm(FlaskForm):
    login = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rep_password = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    specialty = StringField('Specialty', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    login = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class JobForm(FlaskForm):
    team_leader = IntegerField("Тим Лидер", validators=[DataRequired()])
    job = StringField("Описание задания", validators=[DataRequired()])
    categories = StringField("Категории")
    work_size = IntegerField("Количество часов для выполнения", validators=[DataRequired()])
    collaborators = StringField("Id членов команды", validators=[DataRequired()])
    start_date = DateTimeField("Дата начала (d.m.Y h.m)", format='%d.%m.%Y %H:%M')
    is_finished = BooleanField('Закончена?')
    submit = SubmitField("Сохранить")

class DepartmentForm(FlaskForm):
    chief = IntegerField("Шеф", validators=[DataRequired()])
    title = StringField("Название ", validators=[DataRequired()])
    members = StringField("Члены", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired()])
    submit = SubmitField("Сохранить")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.login.data,
            age=form.age.data,
            position=form.position.data,
            specialty=form.specialty.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        print("success")
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
    

@app.route("/")
def index():
    session = db_session.create_session()
    jobs = session.query(Jobs)
    return render_template("index.html", title="Миссия Марс", jobs=jobs)


@app.route('/addjob',  methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs()
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.start_date = form.start_date.data
        job.is_finished = form.is_finished.data
        job.categories = list(
                session.query(Category).\
                filter(Category.id.in_(
                            map(str.strip, form.categories.data.split(','))
                       )
                )
            )
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('job_form.html', title='Добавление задания', 
                           form=form)


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobForm()
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == id).first()
        if job and (job.user == current_user or current_user.id == 1):
            form.team_leader.data = job.team_leader
            form.job.data = job.job
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.start_date.data = job.start_date
            form.is_finished.data = job.is_finished
            form.categories.data = ', '.join(map(lambda x: str(x.id), job.categories))
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == id).first()
        if job:
            job.team_leader = form.team_leader.data
            job.job = form.job.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.start_date = form.start_date.data
            job.is_finished = form.is_finished.data
            job.categories.clear()
            job.categories = list(
                session.query(Category).\
                filter(Category.id.in_(
                            map(str.strip, form.categories.data.split(','))
                       )
                )
            )
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('job_form.html', title='Редактирование задания', form=form)


@app.route('/delete_job/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_job(id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == id).first()
    if job and (job.user == current_user or current_user.id == 1):
        session.delete(job)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/departments")
def department():
    session = db_session.create_session()
    departments = session.query(Department)
    return render_template("departments.html", title="Список департаментов", departments=departments)


@app.route('/adddepartment',  methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        department = Department()
        department.chief = form.chief.data
        department.title = form.title.data
        department.members = form.members.data
        department.email = form.email.data
        session.add(department)
        session.commit()
        return redirect('/departments')
    return render_template('department_form.html', title='Добавление задания', 
                           form=form)


@app.route('/departments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = DepartmentForm()
    if request.method == "GET":
        session = db_session.create_session()
        department = session.query(Department).filter(Department.id == id).first()
        if department and (department.user == current_user or current_user.id == 1):
            form.chief.data = department.chief
            form.title.data = department.title
            form.members.data = department.members
            form.email.data = department.email
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        department = session.query(Department).filter(Department.id == id).first()
        if department:
            department.chief = form.chief.data
            department.title = form.title.data
            department.members = form.members.data
            department.email = form.email.data
            session.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('department_form.html', title='Редактирование департамента', form=form)


@app.route('/delete_department/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    session = db_session.create_session()
    department = session.query(Department).filter(Department.id == id).first()
    if department and (department.user == current_user or current_user.id == 1):
        session.delete(department)
        session.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1), 
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1', 
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/session_test/')
def session_test():
    if 'visits_count' in flask_session:
        flask_session['visits_count'] = flask_session.get('visits_count') + 1
    else:
        flask_session['visits_count'] = 1
    
    return "visit " + str(flask_session['visits_count'])


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')