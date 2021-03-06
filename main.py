import datetime
from flask import (
    Flask,
    render_template
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required
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


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Сайт фанатов игры Tank Duel")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    regform = RegisterForm()
    if regform.validate_on_submit():
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = db_session.create_session()
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


@app.route("/concept-arts")
def concept_arts():
    images = [("Early-main-menu.png", "Ранняя версия главного меню"),
              ("Grass-1.jpg", "Тайл травы (1)"),
              ("Grass-2.jpg", "Тайл травы (2)"),
              ("Big-tanks.png", "Большие танки :D"),
              ("Black-text.png", "Раньше у нас был чёрный текст в главном меню"),
              ("Bush.png", "Куст (вырезан из игры)"),
              ("Unstandart-tiles.png", "Разрушаемые кирпичи (вырезано из игры)")]
    return render_template("scroolbar_of_imgs.html", imgs=images)


@app.route("/blogs")
def blog():
    images = [("meeting.jpg", "Встреча (без тимлида)")]
    return render_template("scroolbar_of_imgs.html", imgs=images)


@app.route("/mods")
def mods():
    return render_template("scroolbar_of_imgs.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    db_session.global_init("db/users.db")
    app.run(host="localhost")
