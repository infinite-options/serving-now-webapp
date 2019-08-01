#  Prashant Marathay
#  Flask Tutorial Video 5  https://youtu.be/44PvX0Yv368
from datetime import datetime
from main import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load__user(user_id):
    return User.query.get(int(user_id))

# database table definitions
class User(db.Model, UserMixin): # define the table fields for the class below.  Automatically creates a table name of lowercase user
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    firstName = db.Column(db.String(60), nullable=False)
    lastName = db.Column(db.String(60), nullable=False)
    phoneNumber = db.Column(db.String(60), nullable=False)
    zipcode = db.Column(db.String(60), nullable=False)
    state = db.Column(db.String(60), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    street = db.Column(db.String(60), nullable=False)
    kitchenName = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    closeTime = db.Column(db.String(60), nullable=False)
    openTime = db.Column(db.String(60), nullable=False)
    deliveryOpenTime = db.Column(db.String(60), nullable=False)
    deliveryCloseTime = db.Column(db.String(60), nullable=False)
    pickup = db.Column(db.Boolean(60), nullable=False)
    delivery = db.Column(db.String(60), nullable=False)
    reusable = db.Column(db.String(60), nullable=False)
    disposable = db.Column(db.String(60), nullable=False)
    canCancel = db.Column(db.String(60), nullable=False)
    # backref creates a relationship that allows us to get author attribute.  Lazy is when it loads the data.  Allows for pulling all posts from an author
    # posts is not a column.  It is the relationship table creation that runs as necessary (lazy)
    # Posts is uppercase since we are referencing the actual POST class

    # Reference for object oriented programming in Python
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
