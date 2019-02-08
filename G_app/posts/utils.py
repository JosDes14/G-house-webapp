import os
import random
import string
import sys
from PIL import Image
from G_app.models import User, Post, Chug, Notification
from flask import app, url_for
from flask_login import current_user
from G_app import db
from datetime import datetime

def member_ls():
    members = User.query.all()
    members.pop(5)
    return members


def get_choices():
    choices = []
    users = User.query.all()
    for user in users:
        username = user.username
        if username != 'admin' and user != current_user:
            choices.append((username, username))
    return choices


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


def random_filename(n):
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(n))


def save_picture(form_picture, relative_path, width, height):
    random_hex = random_filename(15)
    _, file_ext = os.path.splitext(form_picture.filename)
    filename = random_hex + file_ext
    path = os.path.join(app.root_path, relative_path, filename)
    pic_size = (width, height)
    pic = Image.open(form_picture)
    pic.thumbnail(pic_size)
    pic.save(path)
    return filename


def number_voted(post_id):
    voters = voter_dict()
    return len(voters[post_id])


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


def create_bet_post(bet):
    if not bet.bettaker:
        bettaker = "the first person willing to accept it"
        optional = "\nGo to the 'Available bets' section to accept."
    else:
        bettaker = bet.bettaker.username
        optional = ''
    title = "{} has issued a bet to {}! (ID: {})".format(bet.bookmaker.username, bettaker, bet.id)
    content = """Title: {}
Description: {}
Amount: {:.2f} ₲
Odds: {}{}""".format(bet.title, bet.description, bet.amount, bet.odds, optional)
    type = "Bet"
    id_user = 6 #admin
    post = Post(title=title, content=content, type=type, id_user=id_user)
    db.session.add(post)
    db.session.commit()


def accept_bet_post(bet, was_public=False):
    print("accept bet post", file=sys.stdout)


def create_challenge_post(challenge):
    title = "{} has issued a challenge to {}! (ID: {})".format(challenge.challenger.username, challenge.challengee.username, challenge.id)
    content = """Title: {}
Description: {}
Amount: {}.00₲""".format(challenge.title, challenge.description, challenge.amount)
    type = "Challenge"
    id_user = 6 #admin
    post = Post(title=title, content=content, type=type, id_user=id_user)
    db.session.add(post)
    db.session.commit()


def modify_challenge_post(challenge):
    title = "{} has issued a challenge to {}! (ID: {})".format(challenge.challenger.username, challenge.challengee.username, challenge.id)
    post = Post.query.filter_by(title=title).first()
    if challenge.accepted_by_challenger:
        modifier = challenge.challenger
    else:
        modifier = challenge.challengee
    content = """Title: {}
Description: {}
Amount: {}.00₲
({} has modified the challenge)""".format(challenge.title, challenge.description, challenge.amount, modifier.username)
    post.content = content
    post.date_posted = datetime.utcnow()
    db.session.commit()


def accept_challenge_post(challenge):
    title = "{} has issued a challenge to {}! (ID: {})".format(challenge.challenger.username, challenge.challengee.username, challenge.id)
    post = Post.query.filter_by(title=title).first()
    content = """Title: {}
Description: {}
Amount: {}.00₲
THIS CHALLENGE HAS BEEN ACCEPTED AND IS ACTIVE""".format(challenge.title, challenge.description, challenge.amount)
    post.content = content
    post.date_posted = datetime.utcnow()
    db.session.commit()


def finish_challenge_post(challenge):
    title = "{} has issued a challenge to {}! (ID: {})".format(challenge.challenger.username, challenge.challengee.username, challenge.id)
    post = Post.query.filter_by(title=title).first()
    content = """Title: {}
Description: {}
Amount: {}.00₲
THIS CHALLENGE IS DONE""".format(challenge.title, challenge.description, challenge.amount)
    post.content = content
    post.date_posted = datetime.utcnow()
    db.session.commit()


def create_bet_notification(bet):
    title = "NEW BET"
    if not bet.bettaker:
        content = "{} has issued a bet to the first person willing to accept!".format(bet.bookmaker.username)
        link = "#"
        users = User.query.all()
        users.pop(5)
        users.remove(bet.bookmaker)
        for user in users:
            user.notification(title=title, content=content, link=link)
    else:
        content = "{} has issued a bet to you.".format(bet.bookmaker.username)
        link = "#"
        bet.bettaker.notification(title=title, content=content, link=link)


def accept_bet_notification(bet, was_public=False):
    print("accept bet notification", file=sys.stdout)


def new_challenge_notification(challenge):
    title = "NEW CHALLENGE"
    content = "{} has issued a challenge to you!".format(challenge.challenger.username)
    link = url_for('posts.edit_challenge', challenge_id = challenge.id)
    challenge.challengee.notification(title=title, content=content, link=link)


def modify_challenge_notification(challenge):
    title = "MODIFY CHALLENGE"
    if challenge.accepted_by_challenger:
        modifier = challenge.challenger
        accepter = challenge.challengee
    else:
        modifier = challenge.challengee
        accepter = challenge.challenger
    content = "{} has modified the challenge!".format(modifier.username)
    link = url_for('posts.edit_challenge', challenge_id = challenge.id)
    accepter.notification(title=title, content=content, link=link)


def accept_challenge_notification(challenge):
    title = "ACCEPT CHALLENGE"
    content = "The challenge: '{}' has been accepted!".format(challenge.title)
    link = url_for('posts.challenge', challenge_id=challenge.id)
    users = User.query.all()
    users.pop(5)
    for user in users:
        user.notification(title=title, content=content, link=link)


def finish_challenge_notification(challenge):
    title = "FINISH CHALLENGE"
    content = "The challenge: '{}' has {}been completed"
    link = url_for('posts.challenge', challenge_id=challenge.id)
    if challenge.won:
        content = content.format(challenge.title, "")
    else:
        content = content.format(challenge.title, "not ")
    users = User.query.all()
    users.pop(5)
    for user in users:
        user.notification(title=title, content=content, link=link)


def pending_active_challenges(challenges):
    pendings = []
    actives = []
    for challenge in challenges:
        if challenge.active and (not challenge.accepted_by_challenger or not challenge.accepted_by_challengee):
            pendings.append(challenge)
        elif challenge.active and challenge.accepted_by_challenger and challenge.accepted_by_challengee:
            actives.append(challenge)
    return pendings, actives


def create_post_notifications(post):
    if post.type != 'General':
        users = User.query.all()
        for user in users:
            if post.type == 'Request':
                content = "{} has made a request post. Please rate to see if he really deserves that ₲₲₲..."
            else:
                content = "{} is the target of a {} post. HAHAHA, please rate!"
            if user != post.target:
                if post.type == 'Request':
                    content = content.format(post.target.username)
                else:
                    content = content.format(post.target.username, post.type)
            else:
                if post.type == 'Request':
                    content = "You thought this was a legit notification; it isn't! But let's hope your request goes down well with the other goats..."
                else:
                    content = "You are the target of a {} post! Uh oh...".format(post.type)
            title = post.id
            user_id = user.id
            notification = Notification(title=title, content=content, user_id=user_id)
            db.session.add(notification)
            db.session.commit()


def delete_post_notifications(post):
    notifications = Notification.query.filter_by(title=str(post.id))
    for notification in notifications:
        db.session.delete(notification)
        db.session.commit()
