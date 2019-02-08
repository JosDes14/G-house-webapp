from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from G_app.config import Config
from flask_apscheduler import APScheduler

'''
flask
flask-wtf
flask-sqlalchemy
flask-login
flask-bcrypt
flask-mail
Pillow
'''

app = Flask(__name__)

app.config['SECRET_KEY'] = '09141e18147de59340b72a2db35ba8e6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'goathouse.pwdreset@gmail.com'
app.config['MAIL_PASSWORD'] = 'G0@thouse-r3s3tt3r'
mail = Mail(app)

app.jinja_env.add_extension('jinja2.ext.do')

from G_app.users.routes import users
app.register_blueprint(users)

from G_app.posts.routes import posts
app.register_blueprint(posts)

from G_app.main.routes import main
app.register_blueprint(main)
