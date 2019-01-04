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
    posts = db.relationship('Post', backref='author', lazy=True)
    chugs_give = db.relationship('Chug', backref='giver', lazy=True, foreign_keys='Chug.id_giver')
    chugs_take = db.relationship('Chug', backref='taker', lazy=True, foreign_keys='Chug.id_taker')

    def __repr__(self):
        return "User({}, {}, {}, {}, {})".format(self.username, self.email, self.status, self.bucks, self.task)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Post({} | {})".format(self.title, self.date_posted)


class Chug(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, default='CHUG GIVEN!')
    date_given = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_taker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_giver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Chug(ID taker: {}; ID giver: {})".format(self.id_taker, self.id_giver)
