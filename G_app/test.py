from G_app import db
from G_app.models import User, Post, Chug

print(User.query.all())
