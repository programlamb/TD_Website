import datetime
from flask import (
    Flask,
    render_template,
    make_response,
    jsonify
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.utils import redirect
from data.register import RegisterForm
from data.login import LoginForm
from data.users import User
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)


login_manager = LoginManager()
login_manager.init_app(app)


# Функция опознования пользователя
@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).get(user_id)


# Главная страница
# http://localhost:5000/
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Сайт фанатов игры Tank Duel")


# Страница регистрации
# http://localhost:5000/register
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    regform = RegisterForm()
    if regform.validate_on_submit():
        # Обработка ошибок
        if regform.password.data != regform.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=regform,
                                   message='Пароли не совпадают')
        db = db_session.create_session()
        if db.query(User).filter(User.email == regform.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=regform,
                                   message='Такой пользователь уже есть')
        user = User()
        user.name = regform.name.data
        user.email = regform.email.data
        user.set_password(regform.password.data)
        db.add(user)
        db.commit()
        return redirect('/login')
    return render_template(
        'register.html',
        title='Регистрация',
        form=regform
    )


# Страница личного кабинета и входа в аккаунт
# http://localhost:5000/login
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = db_session.create_session()
    # если пользователь не авторизовался
    if not current_user.is_authenticated:
        # Создаём форму регистрации
        form = LoginForm()
        if form.validate_on_submit():
            # Обработка ошибок входа
            user = db.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template(
                'login.html',
                message="Неправильный логин или пароль",
                form=form
            )
        return render_template(
            'login.html',
            title='Авторизация',
            form=form
        )
    else:
        # иначе открывем модальное окно с личным кабинетом
        return render_template('office.html')


# Страница консепт артов
# http://localhost:5000/concept-arts
@app.route("/concept-arts")
def concept_arts():
    # список постов с названиями картинок и заголовками
    images = [("Early-main-menu.png", "Ранняя версия главного меню"),
              ("Grass-1.jpg", "Тайл травы (1)"),
              ("Grass-2.jpg", "Тайл травы (2)"),
              ("Big-tanks.png", "Большие танки :D"),
              ("Black-text.png", "Раньше у нас был чёрный текст в главном меню"),
              ("Bush.png", "Куст (вырезан из игры)"),
              ("Unstandart-tiles.png", "Разрушаемые кирпичи (отменено в ходе разработки)")]
    return render_template("scroolbar_of_imgs.html", imgs=images)


# Страница блога команды
# http://localhost:5000/blogs
@app.route("/blogs")
def blog():
    # список постов с названиями картинок и заголовками
    images = [("meeting.jpg", "Встреча (без тимлида)")]
    return render_template("scroolbar_of_imgs.html", imgs=images)


# Страница для модов
# http://localhost:5000/mods
@app.route("/mods")
def mods():
    # список с названием модификации, её описанием, матерьялами, имем создателя и датой создания
    modifications = [("Snow mod", '''Данный мод заменяет текстуру травы на снег.
                                     \nУстановка:
                                     \n1. Скачать данную картинку;
                                     \n2. Переименовать её в "grass.png";
                                     \n3. Заменить файл с таким же названием в папке pic.''',
                      "snow.png", "parselt134", "21.04.22")]
    return render_template("mods.html", mods=modifications)


# Функция выхода из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# Функция обработки ошибки 404
@app.errorhandler(404)
def not_found():
    """Обработка ошибки 404"""
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    db_session.global_init("db/users.db")
    app.run(host="localhost")