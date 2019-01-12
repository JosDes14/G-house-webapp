from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from G_app.users.forms import LoginForm, UpdateForm, RequestResetForm, ResetPasswordForm
from G_app.models import User, Post, Chug, Groceries
from G_app import db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from G_app.users.utils import *

users = Blueprint('users', __name__)

@users.route("/login", methods=['GET','POST'])
def login():
    chug = chug_matrix()
    members = member_ls()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login not successful. Check email and password.", 'danger')
    return render_template('login.html', title='Login', form=form, members=members, chug=chug)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/user/<username>")
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


@users.route("/account", methods=['GET','POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    user_image = url_for('static', filename="profile_pics/{}".format(current_user.image))
    return render_template('account.html', title='Account', members=members, chug=chug, user_image=user_image, form=form)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('home')
    chug = chug_matrix()
    members = member_ls()
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with reset instructions.", 'info')
        return redirect(url_for('users.login'))
    return render_template('request_reset.html', chug=chug, members=members, form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('home')
    chug = chug_matrix()
    members = member_ls()
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", 'danger')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", 'success')
        return redirect('login')
    return render_template('reset_token.html', chug=chug, members=members, form=form)


@users.route("/update_status/id/<user_id>", methods=['POST'])
def update_status(user_id):
    user = User.query.get_or_404(user_id)
    status = request.form.get('status')
    user.status = status.capitalize()
    db.session.commit()
    return ""
