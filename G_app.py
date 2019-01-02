from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm


app = Flask(__name__)
app.config['SECRET_KEY'] = '09141e18147de59340b72a2db35ba8e6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)



class User(db.Model):
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

#Dummy data. This will be put in database later

chug = [ #Jostijn, Samy, Herbert, Eash, Joe
    [None, 0, 0, 0, 0], #chugs given to Jostijn
    [100, None, 0, 0, 0], #chugs given to Samy
    [0, 0, None, 0, 0], #chugs given to Herbert
    [0, 0, 0, None, 0], #chugs given to Eash
    [0, 0, 0, 0, None]  #chugs given to Joe
]

members = [
    {
        'name': 'Jostijn Dessing',
        'username': 'Jostijn',
        'home': True,
        'task': 'Dishes',
        'bucks': 100,
        'status': 'home'
    },
    {
        'name': 'Samy Naydenov',
        'username': 'Samy',
        'home': False,
        'task': 'Kitchen',
        'bucks': 100,
        'status': 'holiday'
    },
    {
        'name': 'Herbert van Even',
        'username': 'Herbert',
        'home': False,
        'task': 'Floor',
        'bucks': 100,
        'status': 'holiday'
    },
    {
        'name': 'Easwaar Alagesen',
        'username': 'Eash',
        'home': False,
        'task': 'Groceries',
        'bucks': 100,
        'status': 'sleep'
    },
    {
        'name': 'Joseph Corr',
        'username': 'Joe',
        'home': False,
        'task': 'Trash',
        'bucks': 100,
        'status': 'holiday'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', members=members, chug=chug)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "test@mail.com" and form.password.data == "password":
            return redirect(url_for('home'))
        else:
            flash("Login not successful. Check email and password.", 'danger')
    return render_template('login.html', title='Login', form=form, members=members, chug=chug)

@app.route("/about")
def about():
    return "We are the Goathouse (named after a beautiful artwork hanging inside)... Our house consists of 5 sensual males!"
