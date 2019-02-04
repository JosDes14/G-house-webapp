from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from G_app import db, login_manager, app
from flask_login import UserMixin


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
    comments = db.relationship('Comment', backref='original_post', lazy=True)

    def __repr__(self):
        return "Post({} | {})".format(self.title, self.date_posted)


class Chug(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='CHUG GIVEN!')
    date_given = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_taken = db.Column(db.DateTime)
    taken = db.Column(db.Boolean, nullable=False, default=False)
    id_taker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_giver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Chug(ID taker: {}; ID giver: {})".format(self.id_taker, self.id_giver)


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
    description = db.column(db.String(200))
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
    id_challenger = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_challengee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Challenge({} |  by {} to {})".format(self.title, self.id_challenger, self.id_challengee)


class Bet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    accepted_by_bookmaker = db.Column(db.Boolean, nullable=False, default=True)
    accepted_by_bettaker = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    win_claim = db.Column(db.Boolean)
    won = db.Column(db.Boolean)
    amount = db.Column(db.Integer, nullable=False)
    odds = db.Column(db.Integer, nullable=False)
    id_bookmaker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_bettaker= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Bet({} | Bookmaker: {} - Taker: {})".format(self.title, self.id_bookmaker, self.id_bettaker)


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
