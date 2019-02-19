import sys
import json
from flask import render_template, url_for, flash, redirect, request, jsonify, abort, Blueprint
from wtforms import RadioField
from G_app.posts.forms import PostForm, PostFormGeneral, ChallengeForm, EditChallengeForm, BetForm, EditBetForm
from G_app.models import User, Post, Challenge, Bet
from G_app import db, scheduler
from flask_login import current_user, login_required
from G_app.posts.utils import *
from datetime import datetime, timedelta

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
    return dict(chug_matrix=chug, members=members)


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



@posts.route("/bet_completed", methods=["POST"])
@login_required
def bet_completed():
    bet_id = json.loads(request.form.get('bet_id'))
    is_verification = json.loads(request.form.get('is_verification'))
    bet_won = json.loads(request.form.get('bet_won'))
    bet = Bet.query.get_or_404(bet_id)
    if is_verification:
        bet.won = bet_won
        bet.active = False
        bet.finish_notification()
        bet.finish_post()
        if bet.won:
            amount = bet.odds*bet.amount - bet.amount
            bet.bookmaker.transfer(recipient=bet.bettaker, amount=amount, title="Bet transfer")
        else:
            bet.bettaker.transfer(recipient=bet.bookmaker, amount=bet.amount, title="Bet transfer")
    else:
        bet.win_claim = True
        content = "{} claims to have won the bet '{}'".format(bet.bettaker.username, bet.title)
        link = url_for('posts.my_bets')
        bet.bookmaker.notification(title="BET WIN CLAIM", content=content, link=link)
    return jsonify({ 'content' : 'success' })




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
        bet.create_post()
        bet.create_notification()
        flash("Successfully created bet", 'success')
        return redirect(url_for('main.home'))
    return render_template('new_bet.html', form=form)



@posts.route("/edit/bet/id/<int:bet_id>", methods=['GET', 'POST'])
@login_required
def edit_bet(bet_id):
    bet = Bet.query.get_or_404(bet_id)
    if bet.accepted_by_bookmaker and bet.accepted_by_bettaker or\
    current_user not in {bet.bettaker, bet.bookmaker} or\
    current_user == bet.bookmaker and bet.accepted_by_bookmaker or\
    current_user == bet.bettaker and bet.accepted_by_bettaker or\
    not bet.active:
        abort(403)
    form = EditBetForm()
    if form.validate_on_submit():
        if bet.description == form.description.data and bet.amount == form.amount.data and bet.odds == form.odds.data:
            bet.accepted_by_bettaker = True
            bet.accepted_by_bookmaker = True
            bet.accept_post()
            bet.accept_notification()
            flash("The bet has been accepted successfully", 'success')
        else:
            bet.description = form.description.data
            bet.amount = form.amount.data
            bet.odds = form.odds.data
            bet.accepted_by_bettaker = not bet.accepted_by_bettaker
            bet.accepted_by_bookmaker = not bet.accepted_by_bookmaker
            bet.modify_post()
            bet.modify_notification()
            flash("Modified bet", 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'POST':
        key = request.form.get('delete_key')
        if key == "D3l3t3":
            bet.active = False
            db.session.commit()
        flash("Bet refused", 'danger')
    elif request.method == 'GET':
        form.description.data = bet.description
        form.amount.data = bet.amount
        form.odds.data = bet.odds
    return render_template('edit_bet.html', form=form, bet=bet)



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
        bet.accepted_by_bettaker = True
        db.session.commit()
        bet.accept_post(was_public=True)
        bet.accept_notification(was_public=True)
        return jsonify({ 'user' : user.username, 'bet' : bet.title })
    return render_template('available_bets.html', bets=bets)



@posts.route("/my_bets")
@posts.route("/my_bets/page_m=<int:page_m>/page_t=<int:page_t>")
@login_required
def my_bets(page_m=1, page_t=1):
    bets_made = Bet.query.filter_by(id_bookmaker=current_user.id).order_by(Bet.date.desc()).paginate(page=page_m, per_page=5)
    bets_target = Bet.query.filter_by(id_bettaker=current_user.id).order_by(Bet.date.desc()).paginate(page=page_t, per_page=5)
    bets_pending, bets_active = pending_active_bets(current_user.bets_made + current_user.bets_taken)
    return render_template('my_bets.html', bets_made=bets_made, bets_target=bets_target, bets_pending=bets_pending, bets_active=bets_active)



@posts.route("/all_bets")
@login_required
def all_bets():
    page = request.args.get('page', 1, type=int)
    bets = Bet.query.order_by(Bet.date.desc()).paginate(page=page, per_page=10)
    return render_template('all_bets.html', bets=bets)



@posts.route("/bet/id/<int:bet_id>")
@login_required
def bet(bet_id):
    bet = Bet.query.get_or_404(bet_id)
    return render_template("bet.html", bet=bet)



@posts.route("/challenge/id/<int:challenge_id>")
@login_required
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
    current_user == challenge.challengee and challenge.accepted_by_challengee or\
    not challenge.active:
        abort(403)
    form = EditChallengeForm()
    if form.validate_on_submit():
        if form.description.data == challenge.description and form.amount.data == challenge.amount and challenge.time_limit == form.time_limit.data:
            challenge.accepted_by_challenger = True
            challenge.accepted_by_challengee = True
            challenge.accept_post()
            challenge.accept_notification()
            scheduler.add_job(func=challenge_out_of_time, args=[challenge.id], trigger='date', run_date=challenge.time_limit, id='chal'+str(challenge.id))
            flash("The challenge has been accepted", "success")
        else:
            challenge.description = form.description.data
            challenge.amount = form.amount.data
            challenge.time_limit = form.time_limit.data
            challenge.accepted_by_challenger = not challenge.accepted_by_challenger
            challenge.accepted_by_challengee = not challenge.accepted_by_challengee
            challenge.modify_post()
            challenge.modify_notification()
            flash("Modified challenge", 'success')
        db.session.commit()
        return redirect(url_for('main.home'))
    elif request.method == 'POST':
        key = request.form.get('delete_key')
        if key == "D3l3t3":
            challenge.active = False
            db.session.commit()
        flash("Challenge refused", 'danger')
    elif request.method == 'GET':
        form.description.data = challenge.description
        form.amount.data = challenge.amount
        form.time_limit.data = challenge.time_limit
    return render_template('edit_challenge.html',form=form, challenge=challenge)



@posts.route("/challenge_completed", methods=['POST'])
@login_required
def challenge_completed():
    challenge_id = json.loads(request.form.get('challenge_id'))
    is_verification = json.loads(request.form.get('is_verification'))
    completed = json.loads(request.form.get('completed'))
    challenge = Challenge.query.get_or_404(challenge_id)
    if is_verification:
        challenge.won = completed
        challenge.active = False #dont need to commit db because db.session.commit() is called in transfer method
        challenge.finish_post()
        challenge.finish_notification()
        if completed:
            challenge.challenger.transfer(recipient=challenge.challengee, amount=challenge.amount, title="Challenge transfer")
        else:
            challenge.challengee.transfer(recipient=challenge.challenger, amount=challenge.amount, title="Challenge transfer")
    else:
        scheduler.remove_job('chal'+str(challenge_id))
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
        challenge = Challenge(title=form.title.data, description=form.description.data, amount=form.amount.data, time_limit=form.time_limit.data, id_challenger=current_user.id, id_challengee=id_challengee)
        db.session.add(challenge)
        db.session.commit()
        challenge.create_post()
        challenge.create_notification()
        #scheduler.add_job(func=challenge_out_of_time, args=[challenge.id], trigger='date', run_date=form.time_limit.data, id='chal'+str(challenge.id))
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.time_limit.data = datetime.today() + timedelta(days=1)
    return render_template('new_challenge.html', form=form)
