import os
import random
import string
from PIL import Image
from flask import url_for
from flask_mail import Message
from G_app import mail, app, db
from G_app.models import User, Chug, Total
from flask_login import current_user


def send_reset_email(user):
    body = '''Hello {},\n
The team here at Goathouse has received your password reset request.
In order to reset your password please visit the following link: {}.\n
Kind regards,\n
The Goathouse team'''
    token = user.get_reset_token()
    message = Message("Password reset request - GOATHOUSE", sender='goathouse.pwdreset@gmail.com', recipients=[user.email])
    message.body = body.format(user.username, url_for('users.reset_token', token=token, _external=True))
    mail.send(message)


def member_ls():
    members = User.query.all()
    members.pop(5)
    return members


def chug_matrix():
    matrix = [
        [None, 0, 0, 0, 0],
        [0, None, 0, 0, 0],
        [0, 0, None, 0, 0],
        [0, 0, 0, None, 0],
        [0, 0, 0, 0, None]
    ]
    chugs_to_be_taken = Chug.query.filter(Chug.active==True, Chug.accepted==True).all()
    for chug in chugs_to_be_taken:
        matrix[chug.id_taker - 1][chug.id_giver - 1] += 1
    return matrix


def random_filename(n):
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(n))


def save_picture(form_picture, relative_path, width, height):
    random_hex = random_filename(30)
    _, file_ext = os.path.splitext(form_picture.filename)
    filename = random_hex + file_ext
    path = os.path.join(app.root_path, relative_path, filename)
    pic_size = (width, height)
    pic = Image.open(form_picture)
    pic.thumbnail(pic_size)
    pic.save(path)
    return filename


def delete_old_picture():
    path = os.path.join(app.root_path, 'static/profile_pics', current_user.image)
    if os.path.exists(path):
        os.remove(path)


def accept_chug(chug_id):
    chug = Chug.query.get(chug_id)
    chug.accepted = True
    db.session.commit()
    chug.auto_accept_notification()


def chug_price():
    total = Total.query.order_by(Total.date.desc()).first()
    if not total:
        total = 500
    return 0.1*total
