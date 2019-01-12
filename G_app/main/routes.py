from flask import render_template, url_for, flash, redirect, request, jsonify, abort, Blueprint
from G_app.models import User, Post, Groceries
from G_app import db
from flask_login import current_user, login_required
from G_app.main.utils import *

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
    voters = voter_dict()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    chug = chug_matrix()
    members = member_ls()
    return render_template('home.html', members=members, chug=chug, posts=posts, voters=voters)


@main.route("/groceries")
@login_required
def groceries():
    members = member_ls()
    chug = chug_matrix()
    groceries = Groceries.query.all()
    return render_template('groceries.html', members=members, chug=chug, groceries=groceries)


@main.route("/update_groceries", methods=['POST'])
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


@main.route("/about")
def about():
    return str(voter_dict())
