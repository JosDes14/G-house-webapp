import sys
import json
from flask import render_template, url_for, flash, redirect, request, jsonify, abort, Blueprint
from wtforms import RadioField
from G_app.posts.forms import PostForm, PostFormGeneral, ChallengeForm, EditChallengeForm, BetForm
from G_app.models import User, Post, Challenge, Bet
from G_app import db, scheduler
from flask_login import current_user, login_required
from G_app.posts.utils import *
from datetime import datetime

posts = Blueprint('posts', __name__)

'''
def add_post():
    post = Post(title='shit dawg', content='scheduler is working!', id_user=1)
    db.session.add(post)
    db.session.commit()
'''
#scheduler.add_job(func=add_post, trigger='date', run_date=datetime(2019,1,16,0,34,30), id='test')


@posts.context_processor
def context_processor():
    chug = chug_matrix()
    members=member_ls()
    return dict(chug=chug, members=members)


@posts.route("/post_rating", methods=['POST'])
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


@posts.route("/delete_post", methods=['POST'])
def delete_post():
    post_id = request.form.get('post_id')
    post = Post.query.get_or_404(int(post_id))
    delete_post_notifications(post)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message" : "Successfully deleted post"})


@posts.route("/edit/post/id/<post_id>", methods=['GET','POST'])
@login_required
def edit_post(post_id):
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
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        if post.type != "General":
            form.target.data = post.target.username
    return render_template('update_post.html', form=form, post_type=post.type)



@posts.route("/new/post/<post_type>", methods=['GET', 'POST'])
@login_required
def new_post(post_type):
    if not post_type in ['General', 'Request']:
        setattr(PostForm, 'target', RadioField('Choose Target', choices=get_choices()))
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
            if post_type == 'Request':
                id_target = current_user.id
            else:
                id_target = User.query.filter_by(username=form.target.data).first().id
            post = Post(title=form.title.data, content=form.content.data, type=post_type, rating=0, can_vote=True, image=picture_file, id_user=current_user.id, id_target=id_target)
        db.session.add(post)
        db.session.commit()
        create_post_notifications(post)
        flash("Your post has been created!", 'success')
        return redirect(url_for('main.home'))
        #post = Post(title=form.title.data, content=form.content.data)
        #if form.picture.data:
            #picture_file = save_picture(form.picture.data, 'static/post_pics')
    #if form.validate_on_submit():
        #flash("Your post has been created!", 'success')
        #return redirect(url_for('main.home'))
    return render_template('create_post.html', form=form, post_type=post_type)



@posts.route("/new/bet", methods=['GET', 'POST'])
@login_required
def new_bet():
    choices = get_choices()
    choices.append(('anyone', 'Anyone'))
    setattr(BetForm, 'target', RadioField('Choose Target', choices=choices))
    form = BetForm()
    if form.validate_on_submit():
        if form.target.data != 'anyone':
            target_id = User.query.filter_by(username=form.target.data).first().id
        else:
            target_id = None
        title = form.title.data
        description = form.description.data
        amount = form.amount.data
        odds = form.odds.data
        bet = Bet(title=title, description=description, amount=amount, odds=odds, id_bookmaker=current_user.id, id_bettaker=target_id)
        db.session.add(bet)
        db.session.commit()
        create_bet_post(bet)
        create_bet_notification(bet)
        flash("Successfully created bet", 'success')
        return redirect(url_for('main.home'))
    return render_template('new_bet.html', form=form)



@posts.route("/available_bets", methods=['GET','POST'])
@login_required
def available_bets():
    bets = Bet.query.filter(Bet.bettaker==None, Bet.bookmaker!=current_user).all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        bet_id = request.form.get('bet_id')
        user = User.query.get(user_id)
        bet = Bet.query.get(bet_id)
        bet.bettaker = user
        accept_bet_notification(bet)
        accept_bet_post(bet, was_public=True)
        db.session.commit()
        return jsonify({ 'user' : user.username, 'bet' : bet.title })
    return render_template('available_bets.html', bets=bets)



@posts.route("/challenge/id/<int:challenge_id>")
def challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template("challenge.html", challenge=challenge)



@posts.route("/all_challenges")
@login_required
def all_challenges():
    page = request.args.get('page', 1, type=int)
    challenges = Challenge.query.order_by(Challenge.date.desc()).paginate(page=page, per_page=10)
    return render_template('all_challenges.html', challenges=challenges)



@posts.route("/my_challenges")
@posts.route("/my_challenges/page_m=<int:page_m>/page_r=<int:page_r>")
@login_required
def my_challenges(page_m=1, page_r=1):
    challenges_made = Challenge.query.filter_by(id_challenger=current_user.id).order_by(Challenge.date.desc()).paginate(page=page_m, per_page=5)
    challenges_received = Challenge.query.filter_by(id_challengee=current_user.id).order_by(Challenge.date.desc()).paginate(page=page_r, per_page=5)
    challenges_pending, challenges_active = pending_active_challenges(current_user.challenges_made + current_user.challenges_received)
    return render_template('my_challenges.html', challenges_pending=challenges_pending, challenges_made=challenges_made, challenges_received=challenges_received, challenges_active=challenges_active)



@posts.route("/edit/challenge/id/<challenge_id>", methods=['GET', 'POST'])
@login_required
def edit_challenge(challenge_id):
    challenge = Challenge.query.get(int(challenge_id))
    if challenge.accepted_by_challenger and challenge.accepted_by_challengee or\
    current_user not in {challenge.challengee, challenge.challenger} or\
    current_user == challenge.challenger and challenge.accepted_by_challenger or\
    current_user == challenge.challenger and challenge.accepted_by_challenger or\
    not challenge.active:
        abort(403)
    form = EditChallengeForm()
    if form.validate_on_submit():
        if form.description.data == challenge.description and form.amount.data == challenge.amount:
            challenge.accepted_by_challenger = True
            challenge.accepted_by_challengee = True
            accept_challenge_post(challenge)
            accept_challenge_notification(challenge)
            flash("The challenge has been accepted", "success")
        else:
            challenge.description = form.description.data
            challenge.amount = form.amount.data
            challenge.accepted_by_challenger = not challenge.accepted_by_challenger
            challenge.accepted_by_challengee = not challenge.accepted_by_challengee
            modify_challenge_notification(challenge)
            modify_challenge_post(challenge)
            flash("Modified challenge", 'success')
        db.session.commit()
        return redirect(url_for('main.home'))
    elif request.method == 'POST':
        key = request.form.get('delete_key')
        if key == "D3l3t3":
            challenge.active = False
            db.session.commit()
    elif request.method == 'GET':
        form.description.data = challenge.description
        form.amount.data = challenge.amount
    return render_template('edit_challenge.html',form=form, challenge=challenge)



@posts.route("/challenge_completed", methods=['POST'])
@login_required
def challenge_completed():
    challenge_id = json.loads(request.form.get('challenge_id'))
    is_verification = json.loads(request.form.get('is_verification'))
    completed = json.loads(request.form.get('completed'))
    challenge = Challenge.query.get_or_404(int(challenge_id))
    if is_verification:
        challenge.won = completed
        challenge.active = False #dont need to commit db because db.session.commit() is called in transfer method
        finish_challenge_notification(challenge)
        finish_challenge_post(challenge)
        if completed:
            challenge.challenger.transfer(recipient=challenge.challengee, amount=challenge.amount, title="Challenge transfer")
    else:
        challenge.win_claim = True #dont need to commit db because db.session.commit() is called in notification method
        content = "{} claims to have won the challenge '{}'".format(challenge.challengee.username, challenge.title)
        link = url_for('posts.my_challenges')
        challenge.challenger.notification(title="CHALLENGE WIN CLAIM", content=content, link=link)
    return jsonify({ 'content' : 'success' })



@posts.route("/new/challenge", methods=['GET', 'POST'])
@login_required
def new_challenge():
    setattr(ChallengeForm, 'target', RadioField('Choose Target', choices=get_choices()))
    form = ChallengeForm()
    if form.validate_on_submit():
        id_challengee = User.query.filter_by(username=form.target.data).first().id
        challenge = Challenge(title=form.title.data, description=form.description.data, amount=form.amount.data, id_challenger=current_user.id, id_challengee=id_challengee)
        db.session.add(challenge)
        db.session.commit()
        create_challenge_post(challenge)
        new_challenge_notification(challenge)
        return redirect(url_for('main.home'))
    return render_template('new_challenge.html', form=form)
