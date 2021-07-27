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
numb = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V', '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X', '11': 'XI', '12': 'XII', '13': 'XIII', '14': 'XIV', '15': 'XV', '16': 'XVI', '17': 'XVII', '18': 'XVIII', '19': 'XIX', '20': 'XX', '21': 'XXI', '0': 'XXII'}

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


class CompForm(FlaskForm):
    date1 = IntegerField('', validators=[DataRequired()])
    month1 = IntegerField('', validators=[DataRequired()])
    age1 = IntegerField('', validators=[DataRequired()])
    date2 = IntegerField('', validators=[DataRequired()])
    month2 = IntegerField('', validators=[DataRequired()])
    age2 = IntegerField('', validators=[DataRequired()])
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


def getchar(a):
    charall = {
        '[1]': 'Сочетание внутренней мягкости и внешней дистанции. Боится показаться всем мягким, слабым, '
               'хотя это многим очевидно и чувствуется. Страх быть человеком без воли и стержня, поэтому  внешне '
               'показывает излишнюю важность, авторитетность, занятость, основная мотивация – быть уважаемым, '
               'большим, опасным. Желание быть лучше кого-то (друга, соседа, жены), постоянно доказывает свой '
               'авторитет. Основная сложность – это закрытость, невозможность понять, что внутри.',
        '[11]': 'Один из самых комфортных характеров, деликатный, мягкий, может быть строгим в сочетании с некоторыми '
                'секторами (здоровье, логика). Зависим от знаков внимания и благодарности (спасибо, извини, '
                'пожалуйста, доброе утро, спокойной ночи). Эти особенности в нем выражены максимально, чувствует свою '
                'значимость посредством постоянного внимания, благодарность ждет постоянно, иногда до абсурда.',
        '[111]': 'Один из самых непредсказуемых характеров, постоянная смена состояний, невозможно предугадать, '
                 'что и когда выступит катализатором для такого перехода: из состояния душевного, гибкого, '
                 'близкого человека в состояние закрытого, эгоистичного, с выраженной дистанцией. В зависимости от '
                 'ситуации это может быть похоже на истерику. Обусловлено слишком легким переходом из одного '
                 'состояния в другое, динамикой. Человек может измениться буквально за секунду: только что он смеялся '
                 'с вами над одной и той же шуткой, а потом вас же отчитывает за плохое чувство юмора. Характер с '
                 'особенностями, поэтому требуется соблюдение определенных правил и границ.',
        '[1111]': 'Характер лидера, золотая середина, человек просто чувствует себя главным, не лучше и не хуже '
                  'других, просто главный и все. Здоровое стремление добиваться результатов, вести за собой других. '
                  'Отсутствует стремление быть главным любой ценой, нет даже мысли, что это не так: я лидер, '
                  'а кто же еще!?!',
        '[11111]': 'Динамичный характер, вспыльчивый, можно сказать, что это утрированная форма 111. Желание '
                   'контролировать все, что его касается, до мелочей. Основная особенность – обозначение и охрана '
                   'своих границ (вещи, разрешенные и запретные темы и т.п.) При нарушении правил легко переходит на '
                   'высокий тон, желая доказать свое превосходство силой, «лучший из лучших». Контроль может '
                   'переходить границы дозволенного (Что? Почему? Куда? Зачем тебе это? А что? Кто это?) Стремление '
                   'иметь все и сразу. Свое мнение первостепенно и оно лучшее из возможных.',
        '[111111]': 'Близок в интерпретации к характеру 1111(Характер лидера, золотая середина, человек просто '
                    'чувствует себя главным, не лучше и не хуже других, просто главный и все. Здоровое стремление '
                    'добиваться результатов, вести за собой других. Отсутствует стремление быть главным любой ценой, '
                    'нет даже мысли, что это не так: я лидер, а кто же еще!?!), однако ко всему вышеперечисленному '
                    'добавляется желание контроля всего, что его касается.',
        '[8]': 'Сектор ослаблен. Человек держит дистанцию, любить умеет, однако круг близких и любимых очень узкий, '
               'не реагирует на слово «должен»(если нет основы и ничего не отзывается в нем), тяжело принимает '
               'неудачи, боится сложностей, не любит рутину, принимает больше, чем отдает; отрицание смерти или '
               'болезни, отрицание своих сложных качеств; затягивает сроки исполнения просьбы, способен подвести, '
               'не доделать, затянуть. Страх лишней ответственности, дистанция от чужих проблем, '
               'обвиняет обстоятельства, но не себя; сухость чувств. Так же это возможность делегировать, что хорошо '
               'для руководящей должности.',
        '[88]': 'Доброта, забота, способность любить большое количество людей, способность делиться, говорить правду, '
                'оперативная реакция на просьбы, долгое терпение, понимание поведения и поступков партнера, '
                'легкое принятие правды и сложных обстоятельств, патриотизм, религиозность, способность решать '
                'проблемы других своими руками, стремление быть в группе. Не чувствует дистанции, гиперопека, '
                'перегрузка правил, тяжело делегирует, отнимает ответственность у близких, многие задачи удаются '
                'легче. Обвиняет себя, но не обстоятельства. Перегрузка правил и заботы у женщин. Занудство, '
                'сложность делегирования, контроль.',
        '[2]': 'Дефицит энергии, неспособность сконцентрироваться на задаче, перенос дел на завтра, на потом, '
               'постоянное чувство хаоса, запарки, чувство тяжести. При остром дефиците нет вкуса жизни(нет вкуса, '
               'нет запаха, нет желаний), нежелание публичности, не хочется общаться много или часто нужен отдых. '
               'Постоянный поиск источника энергии, как следствие риск впасть в зависимость от донора (22/222/2222 и '
               'выше), быстрая потеря результатов, нужны силы для успеха, резкого старта, снижена выносливость, '
               'тяжесть от ведения хозяйства и приготовления пищи, требуется физическая поддержка и помощь. Сложно '
               'чувствует течение времени, тренды, популярное течение, эмоции ослаблены (тихие или сдержанные), '
               'нет желания их выплескивать, экономит силы.',
        '[22]': 'Хороший запас энергии, есть силы для успеха, дает хороший импульс для развития. Быстрая реакция на '
                'любые действия, легкость на подъем, упорство, трудоспособность, желание долго и много общаться, '
                'сильные эмоции (крик, смех), способность чувствовать время тренды (то, что популярно), '
                'системное отношение ко всему что делает, способность концентрироваться на задаче, как следствие '
                'больше сил и времени.',
        '[222]': '«Профицит энергии», слишком большой запас времени и сил, как следствие возникает лень (быстрое '
                 'исполнение задачи, много лишнего времени). Тяжело раскачиваться, человек с таким запасом как титан '
                 '(большой и громоздкий), невероятная трудоспособность, сильный донор позитивной и негативной '
                 'энергии; легко удается хозяйство, упорство и способность доводить до конца начатое.',
        '[4-]': 'Здоровье может быть ослабленным. Неспособность быстро восстанавливаться после травм и болезней, '
               'хронические болезни, врожденные (если нет достаточно энергии), могут быть внешние проблемы: вес, '
               'кожа, волосы, зрение, зубы.  Нет агрессии, возможно негодование, но не агрессия; здоровье должно быть '
               'на постоянном контроле.',
        '[4]': 'Хороший уровень здоровья и способность быстро восстанавливаться после травм и болезней. В норме,  '
                'уровень агрессии умеренный, врожденная способность к защите.',
        '[44]': 'Сила, красота тела, лица, кожи, рост, молодость, стройность долгие годы; сильный голос, в том числе '
                 'для пения. Долгожитель, профессиональные спортивные данные по причине уникального строения тела и '
                 'способности организма быстро восстанавливаться, физическое здоровье тела, физическая выносливость, '
                 'сила.\nНегатив:\nПерегрузка нервной системы, риск развития психосоматических заболеваний (типа '
                 'диабет, болезни ЖКТ, неврозы, психозы, нервные тики, припадки, рак, кардио). Агрессия, гнев, '
                 'ярость, ненависть, раздражение – при условии неиспользованного ресурса 44 (спорт, работа с большим '
                 'количеством общения, пение), агрессия уходит только вербально.',
        '[7-]': 'Не является показателем отсутствия удачи, в этом случае все в руках человека и иногда это '
                'преимущество. Может быть компенсирован (6/66/666 труд) или ЧС11.',
        '[7]': 'Комфортный уровень везения, везет тогда, когда человек заслужил, попросил, создал для этого условия – '
               'вознаграждение приходит быстро.',
        '[77]': 'Сильный фарт, неожиданное, незапланированное везение, внезапный большой куш или постоянное '
                'поступление мелких возможностей на протяжении всей жизни. Такой сектор удача втягивает в '
                'неприятности и тут же спасает. Рассматривается только в сочетаниях, сам по себе такой коэффициент не '
                'гарантирует везение и счастье.',
        '[777]': '«Инженеры жизни», сильный инструмент для достижения любых возможностей, при условии управления им, '
                 'нельзя пускать на самотек; если нет специальных действий, то чаще приносит несчастья и '
                 'разочарования, требует деликатного обращения.',
        '[6-]': 'Не является негативным показателем, в случае отсутствия коэффициента направляет реализацию в '
               'интеллектуальное русло.',
        '[6]': 'Наличие даже одной 6 в секторе труд уже дает сильные возможности в различных областях. И самая '
                'сильная из них – это привлечение внимания.',
        '[666]': 'Этот сектор настолько сильный, что дает сильные возможности в различных областях. И самая сильная '
                 'из них – это привлечение внимания. Сильная способность для влияния на массы людей и на человека в '
                 'целом, склонность к мошенничеству/оккультизм. В поле этого человека вы будете делать, '
                 'что он говорит, потому что вам захочется.',
        '[9]': 'Сектор ослаблен. Ослаблена память, рассеянность, трудность адаптации в новой среде, трудность '
               'иммиграции, возможно использование сленга, косноязычие. Способность быстро отпускать обиды, '
               'трудности в изучении иностранных языков, могут быть трудности с вождением авто (человек водит, '
               'но не мастерски, или на короткие расстояния).',
        '[99]': 'Обидчивость, сильная память, чувство юмора, богатый вокабуляр (множество синонимов в речи), видения, '
                'пограничные состояния, оккультизм, яркие/пророческие сны, быстрая адаптация в новой среде, '
                'сильные способности в изучении иностранных языков.',
        '[5-]': 'Основа для сильно развитой фантазии, не показатель отсутствия логики (логика – это способность к '
                'анализу, данная нам всем эволюцией), творческое начало, все действия хорошо удаются со второй '
                'попытки, сложное восприятие технических наук и терминов, для понимания сложной технической '
                'информации требуется чуть больше времени; нет страха ошибки или страха показаться глупым, '
                'бесхитростность, доверчивость.',
        '[5]': 'Даже одно число в секторе логика дает хорошие показатели и является ценным ресурсом для развития '
               'памяти, изучения иностранных языков, чувства юмора, аналитических способностей; редкие промахи, '
               'но есть страх допустить ошибку.',
        '[55]': 'Очень сильные способности в науке, интуиция, аналитический склад ума, способности, близкие к '
                'гениальности, поэтому сектор требует обязательного использования такого потенциала, '
                'чтобы не перегрузить интеллект; риск алкоголизма; развитие психоэмоциональных расстройств, '
                'по причине бесконечного анализа.',
        '[3]': 'Страхи, фобии, мнительность, поиски переоценки ценностей, трудность принятия решений, '
               'страх перемещения, быстрая потеря интереса, неуверенность в своих силах, поиски авторитетов, '
               'важно мнение окружающих, страх быть хуже других, перепады настроения, короткий период наслаждения, '
               'склонность к поиску быстрых удовольствий (еда, развлечения), страх перемещений и изменений; гнетущие '
               'мысли, частое отрицание. Часто создает себе сложности, проблемы, чтобы потом испытать радость.',
        '[33]': 'Наиболее стабильный коэффициент, уверенность в себе, своих силах, в своих возможностях, '
                'жизнерадостность, гармония, вера в хорошее и надежда на лучшее. Умение наслаждаться моментом, '
                'умение быстро учиться и получать от этого удовольствие. Умение передавать опыт и внутреннее желание '
                'делиться информацией.',
        '[333]': 'Реализует свой талант практически в любой области, наиболее сильный талант преподавателя, '
                 'способность накапливать и передавать опыт. Наиболее подвержен воздействию извне. При отсутствии '
                 'поддержки в детстве переходит в 3/пуст. Нужно обязательно демонстрировать талант и получать '
                 'комплименты, для уверенности в себе.',
    }
    if 8 < len(a['char']) < 11:
        a['char'] = '[111111]'
    if len(a['debt']) > 3:
        a['debt'] = '[88]'
    else:
        a['debt'] = '[8]'
    if len(a['power']) < 4 or (len(a['power']) == 4 and not(len(a['heal']))):
        a['power'] = '[2]'
    elif (len(a['power']) == 4 and len(a['heal'])) or (len(a['power']) == 5 and not(len(a['heal']))):
        a['power'] = '[22]'
    else:
        a['power'] = '[222]'
    if a['heal'] == '[Пусто]':
        a['heal'] = '[4-]'
    elif len(a['heal']) > 4:
        a['heal'] = '[44]'
    if a['luck'] == '[Пусто]':
        a['luck'] = '[7-]'
    elif len(a['luck']) > 5:
        a['luck'] = '[777]'
    if a['work'] == '[Пусто]':
        a['work'] = '[6-]'
    elif a['work'] == '[66]':
        a['work'] = '[6]'
    elif len(a['work']) > 5:
        a['work'] = '[666]'
    if a['mind'] == '[Пусто]':
        a['mind'] = '[9]'
    elif len(a['mind']) > 4:
        a['mind'] = '[99]'
    if a['logic'] == '[Пусто]':
        a['logic'] = '[5-]'
    elif len(a['logic']) > 4:
        a['logic'] = '[55]'
    if a['intr'] == '[Пусто]':
        a['intr'] = '[3]'
    elif len(a['intr']) > 5:
        a['intr'] = '[333]'
    charend = []
    for i in a:
        charend.append(charall[a[i]] if a[i] in charall else None)
    return charend


def getportrait(d, m, y, d1=None, m1=None, y1=None):
    d = d % (22 + int(d == 22))
    y = sum([int(i) for i in str(y)]) % 22
    if d1 and m1 and y1:
        d1 = d1 % (22 + int(d == 22))
        y1 = sum([int(i) for i in str(y1)]) % 22
        p = {'p1': d, 'p2': m, 'p3': y, 'p4': d + m, 'p5': m + y, 'p6': d + 2 * m + y, 'p7': d + m + y, 'p8': d + 3 * m + y, 'p1+': d1, 'p2+': m1, 'p3+': y1, 'p4+': d1 + m1, 'p5+': m1 + y1, 'p6+': d1 + 2 * m1 + y1, 'p7+': d1 + m1 + y1, 'p8+': d1 + 3 * m1 + y1}
        p['p1c'] = p['p1'] + p['p1+']
        p['p2c'] = p['p2'] + p['p2+']
        p['p3c'] = p['p3'] + p['p3+']
        p['p4c'] = p['p4'] + p['p4+']
        p['p5c'] = p['p5'] + p['p5+']
        p['p6c'] = p['p6'] + p['p6+']
        p['p7c'] = p['p7'] + p['p7+']
        p['p8c'] = p['p8'] + p['p8+']
        for i in p:
            p[i] = numb[str(p[i] % 22)]
    else:
        p = {'p1': d, 'p2': m, 'p3': y, 'p4': d + m, 'p5': m + y, 'p6': d + 2 * m + y, 'p7': d + m + y, 'p8': d + 3 * m + y, 'p9': abs(d - m), 'p10': abs(m - y - 22 * (y == 0)), 'p11': abs(abs(d - m) - abs(m - y) + 22 * (int(d == m) - int(y == m))), 'p12': 2 * d + 4 * m + 2 * y, 'p16': 2 * d + 2 * m + 2 * y, 'p21': 3 * d + 5 * m + 3 * y, 'pA': 2 * d + m, 'pB': d + 2 * m, 'pC': 2 * m + y, 'pD': 2 * y + m, 'pE': 2 * d + 3 * m + y, 'pF': d + 3 * m + 2 * y, 'pH': 4 * d + 4 * m + y}
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
    return render_template("matric.html", title="Расчёт матрицы", matr=None, form=form, titleto='Портрет', to="/portrait", char=None)


@app.route("/matriс", methods=['GET', 'POST'])
def matric():
    form = MatricForm()
    try:
        truedate(form.agee.data, form.monthe.data, form.datee.data)
    except:
        return render_template('matric.html', title='Расчёт матрицы', titleto='Портрет', to="/portrait", form=form, matr=None, message="Пожалуйста, заполните поля правильно.", char=None)
    return render_template("matric.html", title="Расчёт матрицы", form=form, titleto='Портрет', to="/portrait", matr=getmatric(form.datee.data, form.monthe.data, form.agee.data), char=None)


@app.route("/matriсharacter", methods=['GET', 'POST'])
def matricharacter():
    form = MatricForm()
    return render_template("matric.html", title="Расчёт матрицы", form=form, titleto='Портрет', to="/portrait", matr=getmatric(current_user.datep, current_user.monthp, current_user.agep), char=getchar(getmatric(current_user.datep, current_user.monthp, current_user.agep)))


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


@app.route("/portraitcomp", methods=['GET', 'POST'])
def portraitcomp():
    form = CompForm()
    if form.validate_on_submit():
        try:
            truedate(form.age1.data, form.month1.data, form.date1.data)
            truedate(form.age2.data, form.month2.data, form.date2.data)
        except:
            return render_template('portraitcomp.html', title='Композит', form=form, titleto='Матрица', to="/", message="Пожалуйста, заполните поля правильно.", portr=None)
        return render_template('portraitcomp.html', title='Композит', form=form, titleto='Матрица', to="/", portr=getportrait(form.date1.data, form.month1.data, form.age1.data, form.date2.data, form.month2.data, form.age2.data))
    return render_template('portraitcomp.html', title='Композит', form=form, titleto='Матрица', to="/", portr=None)


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
    #app.run(port=8080, host='127.0.0.1')