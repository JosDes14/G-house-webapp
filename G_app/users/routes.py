import json
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, jsonify
from G_app.users.forms import LoginForm, UpdateForm, RequestResetForm, ResetPasswordForm
from G_app.models import User, Post, Chug, Groceries
from G_app import db, bcrypt, mail, scheduler
from flask_login import login_user, current_user, logout_user, login_required
from G_app.users.utils import *
from datetime import datetime, timedelta

users = Blueprint('users', __name__)


@users.context_processor
def context_processor():
    chug = chug_matrix()
    members=member_ls()
    return dict(chug_matrix=chug, members=members)



@users.route("/login", methods=['GET','POST'])
def login():
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
    return render_template('login.html', title='Login', form=form)



@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/user/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user_image = url_for('static', filename="profile_pics/{}".format(user.image))
        return render_template('profile.html', user=user, user_image=user_image, chug_price=chug_price())
    else:
        return abort(404)



@users.route("/account", methods=['GET','POST'])
@login_required
def account():
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
    return render_template('account.html', title='Account', user_image=user_image, form=form)



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('home')
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with reset instructions.", 'info')
        return redirect(url_for('users.login'))
    return render_template('request_reset.html', form=form)



@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('home')
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
    return render_template('reset_token.html', form=form)



@users.route("/current_user_id")
@login_required
def current_user_id():
    return jsonify({'id':current_user.id})



@users.route("/update_status/id/<user_id>", methods=['POST'])
def update_status(user_id):
    user = User.query.get_or_404(user_id)
    status = request.form.get('status')
    user.status = status.capitalize()
    db.session.commit()
    return ""



@users.route("/give_chug", methods=['POST'])
def give_chug():
    recipient_id = request.form.get('recipient_id')
    giver_id = request.form.get('giver_id')
    recipient = User.query.get(recipient_id)
    giver = User.query.get(giver_id)
    title = "{} gives {} a chug".format(giver.username, recipient.username)
    chug = Chug(title=title, id_taker=recipient_id, id_giver=giver_id)
    db.session.add(chug)
    db.session.commit()
    giver.deduct(chug_price())
    accept_by_date = datetime.now() + timedelta(seconds=30)
    scheduler.add_job(func=accept_chug, args=[chug.id], trigger='date', run_date=accept_by_date, id='chug'+str(chug.id))
    chug.create_notification()
    return jsonify({ 'content' : 'success' })



@users.route("/respond_chug", methods=['POST'])
def respond_chug():
    chug_id = request.form.get('chug_id')
    accept = json.loads(request.form.get('accept'))
    scheduler.remove_job('chug'+str(chug_id))
    chug = Chug.query.get(chug_id)
    chug.accepted = accept
    if not accept:
        chug.taker.deduct(chug_price())
        chug.active = False
    chug.accept_notification()
    db.session.commit()
    return jsonify({ 'content' : chug.title })



@users.route("/decrease_chug", methods=['POST'])
def decrease_chug():
    id_giver = request.form.get('id_giver')
    id_taker = request.form.get('id_taker')
    chug = Chug.query.filter(Chug.id_taker==id_taker, Chug.id_giver==id_giver, Chug.active==True, Chug.accepted==True).first()
    chug.active = False
    chug.taken = True
    db.session.commit()
    return jsonify({ 'content' : chug.id })



@users.route("/chug/id/<int:chug_id>")
@login_required
def chug(chug_id):
    chug = Chug.query.get_or_404(chug_id)
    return render_template('chug.html', chug=chug, chug_price=chug_price())
