import json
from flask import render_template, url_for, flash, redirect, request, jsonify, abort, Blueprint
from G_app.models import User, Post, Groceries, Notification, WeeklyVote, Vote
from G_app.main import VOTING_WEEKDAY, DEADLINE_MINS, DEADLINE_HOURS
from G_app.main.forms import WeeklyVotingForm
from G_app import db, app, scheduler
from flask_login import current_user, login_required
from G_app.main.utils import *
from datetime import datetime, timedelta

main = Blueprint('main', __name__)



scheduler.add_job(func=start_voting_day, trigger='cron', args=['/voting_page'], day_of_week=VOTING_WEEKDAY, hour=0, minute=55, id='start')
scheduler.add_job(func=submit_votes_if_timelimit, trigger='cron', day_of_week=VOTING_WEEKDAY, hour=0, minute=58, id='submit')



@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
    voters = voter_dict()
    update_voteable_posts(voters)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    chug = chug_matrix()
    members = member_ls()
    return render_template('home.html', members=members, chug=chug, posts=posts, voters=voters)



@main.route("/voting_page", methods=['GET', 'POST'])
@login_required
def weekly_vote():
    chug = chug_matrix()
    members = member_ls()
    form = WeeklyVotingForm()
    vote_names = get_voting_list()
    last_votes = WeeklyVote.query.order_by(WeeklyVote.date.desc()).all()[:5]
    user_voted = current_user.done_weekly_vote
    if len(last_votes) == 0:
        last_voted_hours = 100
    else:
        time_difference = datetime.utcnow() - last_votes[0].date
        last_voted_hours = time_difference.total_seconds()/3600
    if datetime.today().weekday() == VOTING_WEEKDAY and last_voted_hours > 24 and not user_voted and current_user.username != 'admin':
        show_form = True
    else:
        show_form = False
    if form.validate_on_submit():
        for i, username in enumerate(vote_names):
            id_voter = current_user.id
            id_candidate = User.query.filter_by(username=username).first().id
            rating = form.voting_fields[i].form.rating.data
            description = form.voting_fields[i].form.clarification.data
            vote = Vote(id_voter=id_voter, id_candidate=id_candidate, rating=rating, description=description)
            db.session.add(vote)
        current_user.done_weekly_vote = True
        db.session.commit()
        flash('Thanks for your vote mate!', 'success')
        if everyone_voted(): #or past time...
            submit_weekly_vote()
            set_done_vote_false()
            reset_balance()
        return redirect(url_for('main.home'))
    return render_template('weekly_vote.html', members=members, chug=chug, show_form=show_form, user_voted=user_voted, form=form, last_votes=sort_by_rating(last_votes), vote_names=vote_names)


@main.route("/groceries")
@login_required
def groceries():
    members = member_ls()
    chug = chug_matrix()
    groceries = Groceries.query.all()
    return render_template('groceries.html', members=members, chug=chug, groceries=groceries)


@main.route("/update_groceries", methods=['POST'])
@login_required
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


@main.route("/seen_notifications", methods=['POST'])
@login_required
def seen_notifications():
    notification_ids = json.loads(request.form.get('ids'))
    for id in notification_ids:
        notification = Notification.query.get(id)
        notification.seen = True
        db.session.commit()
    return "0"


@main.route("/notifications/user_id/<int:user_id>")
@login_required
def your_notifications(user_id):
    if current_user.id != user_id:
        abort(403)
    chug = chug_matrix()
    members = member_ls()
    all_notifications = current_user.all_notifications()
    return render_template('user_notifications.html', chug=chug, members=members, notifications=all_notifications)



@main.route("/new_notifications")
@login_required
def notifications():
    notifications = current_user.new_notifications()
    return jsonify([{
        'id' : n.id,
        'title' : n.title,
        'content' : n.content,
        'link' : n.link,
        'timestamp' : n.timestamp
    } for n in notifications])
