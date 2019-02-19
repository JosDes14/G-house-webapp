from G_app import db
from G_app.models import User, Groceries, Post, Challenge

'''
old_posts = Post.query.all()
old_challenges = Challenge.query.all()
'''
db.drop_all()
db.create_all()

'''
for post in old_posts:
    db.session.add(post)

for challenge in old_challenges:
    db.session.add(challenge)
'''

groceries = ['Cheese', 'Milk', 'Eggs', 'Toast Bread', 'Brown Bread', 'Rice',
            'Fruit', 'Tomatoes', 'Onions', 'Garlic', 'Cooking Oil', 'Toilet Paper',
            'Kitchen Paper', 'Dishwasher', 'Beer', 'Juice', 'Salt', 'Black Pepper']

for item in groceries:
    grocery = Groceries(name=item)
    db.session.add(grocery)


user_1 = User(username="Jostijn", name="Jostijn Dessing", email="jostijn0714@gmail.com", password="$2b$12$cro6Nsv3xTgl3Eg6A6LNBO68KuOEN4u7g6J3YzZ/CHHBbkcgoUTVC", status="Home", bucks=100, task="Dishes")
user_2 = User(username="Eash", name="Easwaar Alagesen", email="easwaaralagesen@gmail.com", password="$2b$12$cro6Nsv3xTgl3Eg6A6LNBO68KuOEN4u7g6J3YzZ/CHHBbkcgoUTVC", status="Home", bucks=100, task="Kitchen")
user_3 = User(username="Herb", name="Herbert van Even", email="herbertve.za@gmail.com", password="$2b$12$cro6Nsv3xTgl3Eg6A6LNBO68KuOEN4u7g6J3YzZ/CHHBbkcgoUTVC", status="Home", bucks=100, task="Floor")
user_4 = User(username="Joe", name="Joseph Corr", email="josephcorr@yahoo.com", password="$2b$12$cro6Nsv3xTgl3Eg6A6LNBO68KuOEN4u7g6J3YzZ/CHHBbkcgoUTVC", status="Home", bucks=100, task="Trash")
user_5 = User(username="Samy", name="Samy Naydenov", email="samy.a.naydenov@gmail.com", password="$2b$12$cro6Nsv3xTgl3Eg6A6LNBO68KuOEN4u7g6J3YzZ/CHHBbkcgoUTVC", status="Home", bucks=100, task="Groceries")
user_6 = User(username="admin", name="Administration", email="jostijndessing@gmail.com", password="$2b$12$cro6Nsv3xTgl3Eg6A6LNBO68KuOEN4u7g6J3YzZ/CHHBbkcgoUTVC", status="Home", bucks=10000, task="")
db.session.add(user_1)
db.session.add(user_2)
db.session.add(user_3)
db.session.add(user_4)
db.session.add(user_5)
db.session.add(user_6)
db.session.commit()
