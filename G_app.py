from flask import Flask, render_template, url_for
from forms import LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '09141e18147de59340b72a2db35ba8e6'

members = [
    {
        'name': 'Jostijn Dessing',
        'home': True,
        'task': 'Dishes',
        'bucks': 100
    },
    {
        'name': 'Samy Naydenov',
        'home': False,
        'task': 'Kitchen',
        'bucks': 100
    },
    {
        'name': 'Herbert van Even',
        'home': False,
        'task': 'Floor',
        'bucks': 100
    },
    {
        'name': 'Easwaar Alagesen',
        'home': False,
        'task': 'Groceries',
        'bucks': 100
    },
    {
        'name': 'Joseph Corr',
        'home': False,
        'task': 'Trash',
        'bucks': 100
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', members=members)

@app.route("/about")
def about():
    return "We are the Goathouse (named after a beautiful artwork hanging inside)... Our house consists of 5 sensual males!"
