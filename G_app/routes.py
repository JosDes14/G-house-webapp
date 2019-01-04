import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from G_app.forms import LoginForm, UpdateForm
from G_app.models import User, Post, Chug
from G_app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

#Dummy data. This will be put in database later

chug = [ #Jostijn, Samy, Herbert, Eash, Joe
    [None, 0, 0, 0, 0], #chugs given to Jostijn
    [100, None, 0, 0, 0], #chugs given to Samy
    [0, 0, None, 0, 0], #chugs given to Herbert
    [0, 0, 0, None, 0], #chugs given to Eash
    [0, 0, 0, 0, None]  #chugs given to Joe
]

members = [
    {
        'name': 'Jostijn Dessing',
        'username': 'Jostijn',
        'home': True,
        'task': 'Dishes',
        'bucks': 100,
        'status': 'home'
    },
    {
        'name': 'Samy Naydenov',
        'username': 'Samy',
        'home': False,
        'task': 'Kitchen',
        'bucks': 100,
        'status': 'holiday'
    },
    {
        'name': 'Herbert van Even',
        'username': 'Herbert',
        'home': False,
        'task': 'Floor',
        'bucks': 100,
        'status': 'holiday'
    },
    {
        'name': 'Easwaar Alagesen',
        'username': 'Eash',
        'home': False,
        'task': 'Groceries',
        'bucks': 100,
        'status': 'sleep'
    },
    {
        'name': 'Joseph Corr',
        'username': 'Joe',
        'home': False,
        'task': 'Trash',
        'bucks': 100,
        'status': 'holiday'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', members=members, chug=chug)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login not successful. Check email and password.", 'danger')
    return render_template('login.html', title='Login', form=form, members=members, chug=chug)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def delete_profile_picture():
    path = os.path.join(app.root_path, 'static/profile_pics', current_user.image)
    if os.path.exists(path):
        os.remove(path)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    filename = random_hex + file_ext
    path = os.path.join(app.root_path, 'static/profile_pics', filename)
    pic_size = (150, 150)
    pic = Image.open(form_picture)
    pic.thumbnail(pic_size)
    pic.save(path)
    return filename


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            delete_profile_picture()
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account information has been updated!", 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    user_image = url_for('static', filename="profile_pics/{}".format(current_user.image))
    return render_template('account.html', title='Account', members=members, chug=chug, user_image=user_image, form=form)


@app.route("/about")
def about():
    return render_template('about.html')
