import bs4
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
import readcompilation
import uploader
from threading import Thread
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

application = Flask(__name__)
application.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'

login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message = "Вы должны быть авторизированны"
login_manager.login_message_category = "success"

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id)



@application.route("/play/<id>", methods=["GET"])
def play(id):
    try:
        songs = readcompilation.get_all_songs(id)
        compilation = readcompilation.get_compilation(id)
        return render_template("compilation.html", title="Play", compilation=compilation, songs=songs)
    except:
        return redirect(url_for('compilations'))

@application.route("/play/", methods=["GET"])
def play_none():
    return redirect(url_for('compilations'))
    
@application.route("/compilations", methods=["GET"])
def compilations():
    try:
        args = request.args.get('filter').replace("+", " ").split(",")
    except:
        args = []
    return render_template("main.html", title="Compilations", args=args, compilations=readcompilation.get_all_compilations(args))

@application.route("/create_compilation", methods=["GET"])
@login_required
def create_compilation():
    return render_template("create_page.html")

@application.route("/upload_compilation", methods=["POST"])
@login_required
def upload_compilation():
    songs_url = request.form.get('songs').split(",")
    name = request.form.get('name')
    photo_url = request.form.get('photo_url')
    tags = request.form.get('tags').split(",")
    author_id = current_user.get_id()
    thread = Thread(target=uploading, args=(tags, name, songs_url, photo_url, author_id))
    thread.start()
    thread.join()

    return render_template("succesfull.html", title="Successful", message="Поздравляем, ваша подборка скоро появиться!")

@application.route("/successful", methods=["GET"])
def successful():
    return render_template("succesfull.html", title="Successful", message="Поздравляем, ваша подборка скоро появиться!")

@application.route("/get_song/<id>", methods=["GET"])
def get_song(id):
    song = readcompilation.get_song(id)
    return song

@application.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        user = readcompilation.getUserByEmail(request.form['email'])
        if user and check_password_hash(user[3], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for('profile'))
        flash("Неверная имя/пароль пара", "error")

    return render_template("login.html", title="Authorization")

@application.route("/delete_compilation/<id>", methods=["GET"])
@login_required
def delete_compilation(id):
    try:
        res = readcompilation.delete_compilation(current_user.get_name(), id)
        if res:
            return render_template("succesfull.html", title="Successful", message="Ваша подборка успешно удаленна!")
        else:
            raise Exception()
    except:
        return render_template('404.html'), 404
    

@application.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['psw']) > 7 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = readcompilation.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрировались", "success")
                return redirect(url_for('login'))
            else:
                flash("Пользователь с таким email/именем уже существует", "error")
        else:
            flash("Поля заполнены некоректно", "error")

    return render_template("register.html", title="Registration")

@application.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@application.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли", "success")
    return redirect(url_for('login'))

@application.route('/')
def index():
    return redirect(url_for('home'), 301)

@application.route('/home')
def home():
    return render_template("home.html", title="Main")

@application.route('/profile')
@login_required
def profile():
    author_id = current_user.get_id()
    return render_template("profile.html", title="Profile",compilations=readcompilation.get_user_compilations(author_id))

@application.context_processor
def inject_user():
    if current_user.is_authenticated:
        return dict(isLogged=current_user.is_authenticated, username=current_user.get_name())
    else:
        return dict(isLogged=current_user.is_authenticated)

def get_tags_from_str(tags):
    return tags.replace("[","").replace("]","").replace("'","").split(", ")
application.jinja_env.globals.update(get_tags_from_str=get_tags_from_str)

def get_songs_amount(songs):
    return len(songs.replace("[","").replace("]","").split(","))
application.jinja_env.globals.update(get_songs_amount=get_songs_amount)

def uploading(tags, name, songs_url, photo_url, author_id):
    uploader.add_songs(songs_url)
    readcompilation.create_compilation(tags, name, songs_url, photo_url, author_id)
    

        

if __name__ == "__main__":
    application.config["WTF_CSRF_ENABLED"] = True
    application.run(host='0.0.0.0')