import os
import random
import string
from PIL import Image
from G_app.models import User, Post, Chug
from flask import app

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
