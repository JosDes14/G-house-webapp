from G_app import db, scheduler
import sys
from flask import url_for
from G_app.models import User, Chug, Post, Total, Vote, WeeklyVote
from flask_login import current_user
from datetime import datetime, timedelta

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
    chugs_to_be_taken = Chug.query.filter_by(taken=False).all()
    for chug in chugs_to_be_taken:
        matrix[chug.id_taker - 1][chug.id_giver - 1] += 1
    return matrix


def get_choices():
    choices = []
    users = User.query.all()
    for user in users:
        username = user.username
        if username != 'admin' and user != current_user:
            choices.append((username, username))
    return choices


def update_status(home, out, sleeping):
    if home:
        current_user.status = "Home"
    elif out:
        current_user.status = "Out"
    elif sleeping:
        current_user.status = "Sleeping"


def sort_by_rating(votes):
    votes.sort(key=lambda x: x.rating, reverse=True)
    return votes


def reset_balance():
    users = User.query.all()
    users.pop(5)
    last_votes = WeeklyVote.query.order_by(WeeklyVote.date.desc()).all()[:5]
    total_rating = sum([vote.rating for vote in last_votes])
    weekly_total = Total.query.order_by(Total.date.desc()).first().amount
    user_total = sum([user.bucks for user in users])
    amount = weekly_total - user_total
    if amount > 0:
        for vote in last_votes:
            amount_to_add = (vote.rating/total_rating)*amount
            vote.subject.add(amount_to_add)
    else:
        new_total = Total(user_total)
        db.session.add(new_total)
        db.session.commit()


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


def get_post_amount():
    total = Total.query.order_by(Total.date.desc()).first()
    if total:
        weekly_total = total.amount
    else:
        weekly_total = 500
    return 0.05 * weekly_total


def adjust_buck_balances(post):
    amount = (post.rating/5) * get_post_amount()
    if post.type == 'Request':
        title = "Request success"
        content = "Your request for G-bucks has come through. You have earned {}₲!".format(round(amount, 2))
        link = url_for('users.profile', username=post.target.username)
        post.target.notification(title, content, link)
        post.target.add(amount)
    else:
        title = "Commission earned"
        content = "You have earned commission on your post. You have earned {}₲!".format(round(0.1*amount, 2))
        post.author.notification(title, content)
        post.author.add(0.1*amount)
        title = "Bucks lost"
        content = "You have lost G-bucks due to your bad behaviour. You have lost {}₲!".format(round(amount, 2))
        post.target.notification(title, content)
        post.target.deduct(amount)


def update_voteable_posts(voters):
    voteable_posts = Post.query.filter_by(can_vote=True).all()
    usernames = []
    users = User.query.all()
    for user in users:
        if user.username != 'admin':
            usernames.append(user.username)
    for post in voteable_posts:
        voted = voters[post.id]
        if voted:
            voted.append(post.target.username)
        else:
            voted = [post.target.username]
        time_difference = datetime.utcnow() - post.date_posted
        time_difference_hours = time_difference.total_seconds()/3600
        if set(voted) == set(usernames) or time_difference_hours > 24:
            adjust_buck_balances(post)
            post.can_vote = False
            db.session.commit()


def get_voting_list():
    users = User.query.all()
    vote_names = []
    for user in users:
        if not user.username in ['admin', current_user.username]:
            vote_names.append(user.username)
    return vote_names


def everyone_voted():
    users = User.query.all()
    for user in users:
        if user.username != 'admin' and not user.done_weekly_vote:
            return False
    return True


def submit_weekly_vote(): #CLEAN THIS UP LAH!!!!!!!!
    users = User.query.all()
    users.pop(5)
    today = datetime.utcnow()
    day_ago = datetime.utcnow() - timedelta(hours=24)
    ratings = [0,0,0,0,0]
    descriptions = ['','','','','']
    voted = [True,True,True,True,True]
    for user in users:
        votes = Vote.query.filter(Vote.date>day_ago).filter_by(id_voter=user.id).all()
        if len(votes) > 0:
            for vote in votes:
                ratings[vote.id_candidate - 1] += vote.rating
                if len(vote.description) > 0:
                    descriptions[vote.id_candidate - 1] += vote.voter.username + '\n' + vote.description + '\n\n'
        else:
            voted[user.id - 1] = False
            for i in range(len(ratings)):
                if i != user.id - 1:
                    ratings[i] += 10
    for i in range(len(ratings)):
        ratings[i] = ratings[i]/4
        weekly_vote = WeeklyVote(task = users[i].task, rating=ratings[i], voted=voted[i], description=descriptions[i], id_subject=i+1)
        db.session.add(weekly_vote)
    db.session.commit()


def submit_votes_if_timelimit():
    last_vote = WeeklyVote.query.order_by(WeeklyVote.date.desc()).first()
    if not last_vote:
        last_voted_hours = 100
    else:
        time_difference = datetime.utcnow() - last_vote.date
        last_voted_hours = time_difference.total_seconds()/3600
    if last_voted_hours > 24:
        submit_weekly_vote()
        set_done_vote_false()
        reset_balance()


def start_voting_day(url):
    users = User.query.all()
    users.pop(5)
    for user in users:
        content = "Hey {}, today is voting day! Time to give everyone a rating... NOW".format(user.username)
        user.notification(title="Voting time!", content=content, link=url)

def set_done_vote_false():
    users = User.query.all()
    for user in users:
        user.done_weekly_vote = False
    db.session.commit()
