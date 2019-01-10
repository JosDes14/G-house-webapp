import os
import sys
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from G_app.forms import LoginForm, UpdateForm, PostForm, PostFormGeneral
from G_app.models import User, Post, Chug, Groceries
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


def save_picture(form_picture, relative_path, width, height):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    filename = random_hex + file_ext
    path = os.path.join(app.root_path, relative_path, filename)
    pic_size = (width, height)
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


def voter_dict():
    posts = Post.query.filter_by(can_vote=True)
    voted = dict()
    for post in posts:
        if post.voted:
            voters = post.voted.split('\n')
        else:
            voters = []
        voted[post.id] = voters
    return voted


def number_voted(post_id):
    voters = voter_dict()
    return len(voters[post_id])


def get_choices():
    choices = []
    users = User.query.all()
    for user in users:
        username = user.username
        if username != 'admin':
            choices.append((username, username))
    return choices


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
    voters = voter_dict()
    posts = Post.query.all()
    posts.reverse()
    chug = chug_matrix()
    members = member_ls()
    return render_template('home.html', members=members, chug=chug, posts=posts, voters=voters)


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


@app.route("/groceries")
@login_required
def groceries():
    members = member_ls()
    chug = chug_matrix()
    groceries = Groceries.query.all()
    return render_template('groceries.html', members=members, chug=chug, groceries=groceries)


@app.route("/update_groceries", methods=['POST'])
def update_groceries():
    was_in_house = request.form.get('prev_in_house')
    item_id = request.form.get('id')
    item = Groceries.query.get(item_id)
    if was_in_house == "False":
        item.in_house = True
    else:
        item.in_house = False
    #item.in_house = True if item_in_house == "True" else item.in_house = False
    db.session.commit()
    return jsonify({"message" : "Updated database"})


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
        return abort(404)


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    chug = chug_matrix()
    members = member_ls()
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'static/profile_pics', 150, 150)
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
    return str(voter_dict())


@app.route("/post_rating", methods=['POST'])
def post_rating():
    rating = request.form.get('rating')
    post_id = request.form.get('post_id')
    post_id = int(post_id)
    rating = int(rating)
    post_num_voted = number_voted(post_id)
    post = Post.query.filter_by(id=int(post_id)).first()
    new_rating = ((post.rating * post_num_voted) + rating)/(post_num_voted + 1)
    post.rating = new_rating
    if post.voted:
        post.voted += '\n'+current_user.username
    else:
        post.voted = current_user.username
    db.session.commit()
    return jsonify({"message" : "Rating: {} | Post ID: {} | data: {}".format(rating, post_id, type(post_id)),
                    "rating" : round(new_rating, 2)})


@app.route("/update_status/id/<user_id>", methods=['POST'])
def update_status(user_id):
    user = User.query.get_or_404(user_id)
    status = request.form.get('status')
    user.status = status.capitalize()
    db.session.commit()
    return ""

@app.route("/edit/post/id/<post_id>", methods=['GET','POST'])
@login_required
def edit_post(post_id):
    chug = chug_matrix()
    members = member_ls()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if post.type != 'General':
        form = PostForm()
    else:
        form = PostFormGeneral()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'static/post_pics', 500, 500)
            post.image = picture_file
        post.title = form.title.data
        post.content = form.content.data
        if post.type != "General":
            id_target = User.query.filter_by(username=form.target.data).first().id
            post.id_target = id_target
        db.session.commit()
        flash("Your post has been updated!", 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        if post.type != "General":
            form.target.data = post.target.username
    return render_template('update_post.html', form=form, members=members, chug=chug, post_type=post.type)


@app.route("/new/post/<post_type>", methods=['GET', 'POST'])
@login_required
def new_post(post_type):
    chug = chug_matrix()
    members = member_ls()
    if post_type != 'General':
        form = PostForm()
    else:
        form = PostFormGeneral()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'static/post_pics', 500, 500)
        else:
            picture_file = None
        if post_type == 'General':
            post = Post(title=form.title.data, content=form.content.data, id_user=current_user.id, image=picture_file)
        else:
            id_target = User.query.filter_by(username=form.target.data).first().id
            post = Post(title=form.title.data, content=form.content.data, type=post_type, rating=0, can_vote=True, image=picture_file, id_user=current_user.id, id_target=id_target)
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
