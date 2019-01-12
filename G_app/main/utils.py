from G_app.models import User, Chug, Post
from flask_login import current_user

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



def get_choices():
    choices = []
    users = User.query.all()
    for user in users:
        username = user.username
        if username != 'admin':
            choices.append((username, username))
    return choices
