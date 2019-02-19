from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for
from datetime import datetime
from G_app import db, login_manager, app
from flask_login import UserMixin
import sys


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String, nullable=False)
    bucks = db.Column(db.Float, nullable=False)
    task = db.Column(db.String, nullable=False)
    done_weekly_vote = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys='Post.id_user')
    posts_targeted = db.relationship('Post', backref='target', lazy=True, foreign_keys='Post.id_target')
    chugs_give = db.relationship('Chug', backref='giver', lazy=True, foreign_keys='Chug.id_giver')
    chugs_take = db.relationship('Chug', backref='taker', lazy=True, foreign_keys='Chug.id_taker')
    notifications = db.relationship('Notification', backref='target', lazy=True)
    payments_made = db.relationship('Transaction', backref='payer', lazy=True, foreign_keys='Transaction.id_payer')
    payments_received = db.relationship('Transaction', backref='payee', lazy=True, foreign_keys='Transaction.id_payee')
    challenges_made =  db.relationship('Challenge', backref='challenger', lazy=True, foreign_keys='Challenge.id_challenger')
    challenges_received =  db.relationship('Challenge', backref='challengee', lazy=True, foreign_keys='Challenge.id_challengee')
    bets_made =  db.relationship('Bet', backref='bookmaker', lazy=True, foreign_keys='Bet.id_bookmaker')
    bets_taken =  db.relationship('Bet', backref='bettaker', lazy=True, foreign_keys='Bet.id_bettaker')
    comments = db.relationship('Comment', backref='commenter', lazy=True)
    votes_made = db.relationship('Vote', backref='voter', lazy=True, foreign_keys='Vote.id_voter')
    votes_received = db.relationship('Vote', backref='candidate', lazy=True, foreign_keys='Vote.id_candidate')
    weekly_votes = db.relationship('WeeklyVote', backref='subject', lazy=True, foreign_keys='WeeklyVote.id_subject')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id' : self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except :
            return None
        return User.query.get(user_id)

    def notification(self, title, content, link="#"):
        notification = Notification(title=title, content=content, link=link, user_id=self.id)
        db.session.add(notification)
        db.session.commit()

    def new_notifications(self):
        return Notification.query.filter_by(user_id=self.id, seen=False).all()

    def all_notifications(self):
        return Notification.query.filter_by(user_id=self.id).order_by(Notification.timestamp.desc()).all()

    def last_notifications(self, n):
        return Notification.query.filter_by(user_id=self.id).order_by(Notification.timestamp.desc()).all()[:n]

    def transfer(self, recipient, amount, title="Here you go", description=None):
        recipient.bucks += amount
        self.bucks -= amount
        transaction = Transaction(title=title, description=description, amount=amount, id_payer=self.id, id_payee=recipient.id)
        db.session.add(transaction)
        db.session.commit()
        content = "{} has transfered you {:.2f} ₲!".format(self.username, amount)
        #link = url_for('main.my_transactions')
        link = "/my_transactions" #hardcoded because app context not always available
        recipient.notification(title="TRANSFER", content=content, link=link)

    def deduct(self, amount):
        admin = User.query.get(6)
        self.bucks -= amount
        admin.bucks += amount
        title = "Deduction: {}".format(self.username)
        transaction = Transaction(title=title, amount=amount, id_payer=self.id, id_payee=admin.id)
        db.session.add(transaction)
        db.session.commit()

    def add(self, amount):
        admin = User.query.get(6)
        if admin.bucks < amount:
            admin.bucks += amount
        self.bucks += amount
        admin.bucks -= amount
        title = "Addition: {}".format(self.username)
        transaction = Transaction(title=title, amount=amount, id_payer=admin.id, id_payee=self.id)
        db.session.add(transaction)
        db.session.commit()

    def __repr__(self):
        return "User({}, {}, {}, {}, {})".format(self.username, self.email, self.status, self.bucks, self.task)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='General')
    rating = db.Column(db.Float)
    can_vote = db.Column(db.Boolean, nullable=False, default=False)
    voted = db.Column(db.String(150))
    image = db.Column(db.String(150))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_target = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_challenge = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    id_bet = db.Column(db.Integer, db.ForeignKey('bet.id'))
    comments = db.relationship('Comment', backref='original_post', lazy=True)

    def __repr__(self):
        return "Post({} | {})".format(self.title, self.date_posted)


class Chug(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='CHUG GIVEN!')
    date_given = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_taken = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable=False, default=True)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    taken = db.Column(db.Boolean, nullable=False, default=False)
    id_taker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_giver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Chug(ID taker: {}; ID giver: {})".format(self.id_taker, self.id_giver)

    def create_notification(self):
        users = User.query.all()
        users.pop(5)
        title = "NEW CHUG"
        for user in users:
            if user == self.taker:
                content = "{} has given you a chug, what will you do?!".format(self.giver.username)
            else:
                content = "{} has given {} a chug!".format(self.giver.username, self.taker.username)
            link = url_for('users.chug', chug_id=self.id)
            user.notification(title=title, content=content, link=link)

    def accept_notification(self):
        users = User.query.all()
        users.pop(5)
        if self.accepted:
            title = "ACCEPT CHUG"
            content = "{} has accepted the chug by {}!!".format(self.taker.username, self.giver.username)
        else:
            title = "REFUSE CHUG"
            content = "{} has spent ₲₲₲ to defend the chug by {}...".format(self.taker.username, self.giver.username)
        link = url_for('users.chug', chug_id=self.id)
        for user in users:
            user.notification(title=title, content=content, link=link)

    def auto_accept_notification(self):
        users = User.query.all()
        users.pop(5)
        title = "ACCEPT CHUG"
        content = "{} has accepted the chug by {} because he didn't respond within a day!".format(self.taker.username, self.giver.username)
        link = "/chug/id/"+str(self.id) #application context is not always available...
        for user in users:
            if user == self.taker:
                content = "You took too long (>24hrs) to respond to the chug by {}, so it has been automatically accepted".format(self.giver.username)
            user.notification(title=title, content=content, link=link)



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='Notification')
    content = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    seen = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Notification({} | {})".format(self.title, self.timestamp)


class Groceries(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    in_house = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "({} | In house: {})".format(self.name, self.in_house)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_payer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_payee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Transaction({} bucks | from {} to {})".format(self.amount, self.id_payer, self.id_payee)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    accepted_by_challenger = db.Column(db.Boolean, nullable=False, default=True)
    accepted_by_challengee = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    win_claim = db.Column(db.Boolean)
    won = db.Column(db.Boolean)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_limit = db.Column(db.DateTime, nullable=False)
    id_challenger = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_challengee = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post', backref='challenge', lazy=True)

    def __repr__(self):
        return "Challenge({} |  by {} to {})".format(self.title, self.id_challenger, self.id_challengee)

    def add_post(self, title, content):
        type = "Challenge"
        id_user = 6
        id_challenge = self.id
        post = Post(title=title, content=content, type=type, id_user=id_user, id_challenge=id_challenge)
        db.session.add(post)
        db.session.commit()

    def post_content(self):
        content = """Title: {}
        Description: {}
        Amount: {}.00 ₲""".format(self.title, self.description, self.amount)
        return content

    def create_post(self):
        title = "{} has issued a challenge to {}"
        if self.challengee:
            title = title.format(self.challenger.username, self.challengee.username)
        else:
            title = title.format(self.challenger.username, "anyone. Be the first to accept it!")
        content = self.post_content()
        self.add_post(title, content)

    def modify_post(self):
        post = self.posts[0]
        post.content = self.post_content()
        post.content += """\nTHIS CHALLENGE HAS BEEN MODIFIED"""
        db.session.commit()

    def accept_post(self):
        title = "The challenge: '{}' has been accepted".format(self.title)
        content = self.post_content()
        self.add_post(title, content)

    def finish_post(self):
        title = "The challenge: '{}' is done".format(self.title)
        content = self.post_content()
        if self.won:
            completed = "completed"
        else:
            completed = "not completed"
        content += """\nThis challenge was {}.""".format(completed)
        self.add_post(title, content)

    def create_notification(self):
        title = "NEW CHALLENGE"
        content = "{} has issued a challenge to you!".format(self.challenger.username)
        link = url_for('posts.edit_challenge', challenge_id = self.id)
        self.challengee.notification(title=title, content=content, link=link)

    def modify_notification(self):
        title = "MODIFY CHALLENGE"
        if self.accepted_by_challenger:
            modifier = self.challenger
            accepter = self.challengee
        else:
            modifier = self.challengee
            accepter = self.challenger
        content = "{} has modified the challenge: '{}'!".format(modifier.username, self.title)
        link = url_for('posts.edit_challenge', challenge_id = self.id)
        accepter.notification(title=title, content=content, link=link)

    def accept_notification(self):
        title = "ACCEPT CHALLENGE"
        content = "The challenge: '{}' has been accepted!".format(self.title)
        link = url_for('posts.challenge', challenge_id = self.id)
        users = User.query.all()
        users.pop(5)
        for user in users:
            user.notification(title=title, content=content, link=link)

    def finish_notification(self):
        title = "FINISH CHALLENGE"
        content = "The challenge: '{}' has {}been completed"
        link = url_for('posts.challenge', challenge_id=self.id)
        if self.won:
            content = content.format(self.title, "")
        else:
            content = content.format(self.title, "not ")
        users = User.query.all()
        users.pop(5)
        for user in users:
            user.notification(title=title, content=content, link=link)



class Bet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    accepted_by_bookmaker = db.Column(db.Boolean, nullable=False, default=True)
    accepted_by_bettaker = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    win_claim = db.Column(db.Boolean)
    won = db.Column(db.Boolean)
    amount = db.Column(db.Integer, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_bookmaker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_bettaker= db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post', backref='bet', lazy=True)

    def __repr__(self):
        return "Bet({} | Bookmaker: {} - Taker: {})".format(self.title, self.id_bookmaker, self.id_bettaker)

    def add_post(self, title, content):
        type = "Bet"
        id_user = 6
        id_bet = self.id
        post = Post(title=title, content=content, type=type, id_user=id_user, id_bet=id_bet)
        db.session.add(post)
        db.session.commit()

    def post_content(self):
        content = """Title: {}
    Description: {}
    Amount: {:.2f} ₲
    Odds: {}""".format(self.title, self.description, self.amount, self.odds)
        return content

    def create_post(self):
        if not self.bettaker:
            bettaker = "the first person willing to accept it"
            optional = "\nGo to the 'Available bets' section to accept."
        else:
            bettaker = self.bettaker.username
            optional = ''
        title = "{} has issued a bet to {}!".format(self.bookmaker.username, bettaker)
        content = self.post_content() + optional
        self.add_post(title, content)

    def create_notification(self):
        title = "NEW BET"
        if not self.bettaker:
            content = "{} has issued a bet to the first person willing to accept!".format(self.bookmaker.username)
            link = url_for('posts.available_bets')
            users = User.query.all()
            users.pop(5)
            users.remove(self.bookmaker)
            for user in users:
                user.notification(title=title, content=content, link=link)
        else:
            content = "{} has issued a bet to you.".format(self.bookmaker.username)
            link = url_for('posts.edit_bet', bet_id=self.id)
            self.bettaker.notification(title=title, content=content, link=link)

    def modify_post(self):
        post = self.posts[0]
        post.content = self.post_content()
        post.content += "\nTHIS BET HAS BEEN MODIFIED"
        db.session.commit()

    def modify_notification(self):
        title = "MODIFY BET"
        if self.accepted_by_bookmaker:
            modifier = self.bookmaker
            accepter = self.bettaker
        else:
            modifier = self.bettaker
            accepter = self.bookmaker
        content = "{} has modified the bet: '{}'!".format(modifier.username, self.title)
        link = url_for('posts.edit_bet', bet_id=self.id)
        accepter.notification(title=title, content=content, link=link)

    def accept_post(self, was_public=False):
        if was_public:
            title = "{} has accepted the public bet from {}"
        else:
            title = "{} has accepted the bet by {}"
        title = title.format(self.bettaker.username, self.bookmaker.username)
        content = self.post_content()
        if was_public:
            content += "\nThis bet is no longer available..."
        self.add_post(title, content)

    def accept_notification(self, was_public=False):
        title = "ACCEPT BET"
        content = "The bet '{}' has been accepted{}"
        if was_public:
            content = content.format(self.title, ", it is no longer available...")
        else:
            content = content.format(self.title, '!')
        link = url_for('posts.bet', bet_id=self.id)
        users = User.query.all()
        users.pop(5)
        for user in users:
            user.notification(title=title, content=content, link=link)
        print("ACCEPT NOTIFICATION", file=sys.stdout)

    def finish_post(self):
        if self.won:
            winner = self.bettaker
        else:
            winner = self.bookmaker
        title = "The bet '{}' is finished".format(self.title)
        content = self.post_content()
        content += "\nThis bet has been won by " + winner.username
        self.add_post(title, content)

    def finish_notification(self):
        if self.won:
            winner = self.bettaker
        else:
            winner = self.bookmaker
        title = "FINISH BET"
        content = "The bet '{}' has been won by {}".format(self.title, winner.username)
        link = url_for('posts.bet', bet_id=self.id)
        users = User.query.all()
        users.pop(5)
        for user in users:
            user.notification(title=title, content=content, link=link)



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return "Comment({} | {})".format(self.content, self.user_id)


class Total(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class WeeklyVote(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    voted = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_subject = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    '''
    task_eash = db.Column(db.String(50), nullable=False)
    rating_eash = db.Column(db.Float, nullable=False)
    voted_eash = db.Column(db.Boolean, nullable=False, default=True)
    description_eash = db.Column(db.Text)

    task_joe = db.Column(db.String(50), nullable=False)
    rating_joe = db.Column(db.Float, nullable=False)
    voted_joe = db.Column(db.Boolean, nullable=False, default=True)
    description_joe = db.Column(db.Text)

    task_samy = db.Column(db.String(50), nullable=False)
    rating_samy = db.Column(db.Float, nullable=False)
    voted_samy = db.Column(db.Boolean, nullable=False, default=True)
    description_samy = db.Column(db.Text)

    task_herb = db.Column(db.String(50), nullable=False)
    rating_herb = db.Column(db.Float, nullable=False)
    voted_herb = db.Column(db.Boolean, nullable=False, default=True)
    description_herb = db.Column(db.Text)
    '''



class Vote(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    id_voter = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_candidate = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
