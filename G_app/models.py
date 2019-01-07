from datetime import datetime
from G_app import db, login_manager
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
    bucks = db.Column(db.Integer, nullable=False)
    task = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys='Post.id_user')
    posts_targeted = db.relationship('Post', backref='target', lazy=True, foreign_keys='Post.id_target')
    chugs_give = db.relationship('Chug', backref='giver', lazy=True, foreign_keys='Chug.id_giver')
    chugs_take = db.relationship('Chug', backref='taker', lazy=True, foreign_keys='Chug.id_taker')
    notifications = db.relationship('Notification', backref='target', lazy=True)
    payments_made = db.relationship('Transaction', backref='payer', lazy=True, foreign_keys='Transaction.id_payer')
    payments_received = db.relationship('Transaction', backref='payee', lazy=True, foreign_keys='Transaction.id_payee')
    challenges_made =  db.relationship('Challenge', backref='challenger', lazy=True, foreign_keys='Challenge.id_challenger')
    challenges_received =  db.relationship('Challenge', backref='challengee', lazy=True, foreign_keys='Challenge.id_challengee')


    def __repr__(self):
        return "User({}, {}, {}, {}, {})".format(self.username, self.email, self.status, self.bucks, self.task)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='General')
    rating = db.Column(db.Integer)
    can_vote = db.Column(db.Boolean, nullable=False, default=False)
    voted = db.Column(db.String(150))
    image = db.Column(db.String(20))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_target = db.Column(db.Integer, db.ForeignKey('user.id'))

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
    active = db.Column(db.Boolean, nullable=False, default=False)
    win_claim = db.Column(db.Boolean)
    won = db.Column(db.Boolean)
    id_challenger = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_challengee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Challenge({} |  by {} to {})".format(self.title, self.id_challenger, self.id_challengee)
