import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from G_app.forms import LoginForm, UpdateForm, PostForm, PostFormGeneral
from G_app.models import User, Post, Chug
from G_app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

#   ---FUNCTIONS---
def member_ls():
    members = []
    users = User.query.all()
    for user in users:
        if user.username != 'admin':
            user_dict = {
                'username': user.username,
                'name': user.name,
                'task': user.task,
                'bucks': user.bucks,
                'status': user.status
            }
            members.append(user_dict)
    return members


def chug_matrix():
    matrix = [
        [None, 0, 0, 0, 0],
        [0, None, 0, 0, 0],
        [0, 0, None, 0, 0],
        [0, 0, 0, None, 0],
        [0, 0, 0, 0, None]
    ]
    chugs_to_be_taken = Chug.query.filter_by(taken=False).all()
    for chug in chugs_to_be_taken:
        matrix[chug.id_taker - 1][chug.id_giver - 1] += 1
    return matrix


def delete_old_picture():
    path = os.path.join(app.root_path, 'static/profile_pics', current_user.image)
    if os.path.exists(path):
        os.remove(path)


def save_picture(form_picture, relative_path):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    filename = random_hex + file_ext
    path = os.path.join(app.root_path, relative_path, filename)
    pic_size = (150, 150)
    pic = Image.open(form_picture)
    pic.thumbnail(pic_size)
    pic.save(path)
    return filename


def update_status(home, out, sleeping):
    if home:
        current_user.status = "Home"
    elif out:
        current_user.status = "Out"
    elif sleeping:
        current_user.status = "Sleeping"


#   ---Routes---
@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    '''if request.method == "POST":
        if 'submit' in request.form:
            status = request.form['status']
            current_user.status = status
            db.session.commit()
            return redirect(url_for('home'))'''
    chug = chug_matrix()
    members = member_ls()
    return render_template('home.html', members=members, chug=chug)


@app.route("/login", methods=['GET','POST'])
def login():
    chug = chug_matrix()
    members = member_ls()
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


@app.route("/user/<username>")
@login_required
def profile(username):
    members = member_ls()
    chug = chug_matrix()
    user = User.query.filter_by(username=username).first()
    if user:
        user_image = url_for('static', filename="profile_pics/{}".format(user.image))
        return render_template('profile.html', members=members, chug=chug, user=user, user_image=user_image)
    else:
        return "user does not exist..."


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    chug = chug_matrix()
    members = member_ls()
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'static/profile_pics')
            if current_user.image != 'default.jpg':
                delete_old_picture()
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


@app.route("/new/post/<post_type>", methods=['GET', 'POST'])
@login_required
def new_post(post_type):
    chug = chug_matrix()
    members = member_ls()
    if post_type != 'general':
        form = PostForm()
    else:
        form = PostFormGeneral()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'static/post_pics')
        else:
            picture_file = None
        if post_type == 'general':
            post = Post(title=form.title.data, content=form.content.data, id_user=current_user.id, image=picture_file)
        else:
            id_target = User.query.filter_by(username=form.target.data).first().id
            post = Post(title=form.title.data, content=form.content.data, type=post_type, rating=0, can_vote=True, image=picture_file, id_user=current_user.id, id_target=id_target, voted=current_user.username+'\n')
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", 'success')
        return redirect(url_for('home'))
        #post = Post(title=form.title.data, content=form.content.data)
        #if form.picture.data:
            #picture_file = save_picture(form.picture.data, 'static/post_pics')
    #if form.validate_on_submit():
        #flash("Your post has been created!", 'success')
        #return redirect(url_for('home'))
    return render_template('create_post.html', form=form, chug=chug, members=members, post_type=post_type)
