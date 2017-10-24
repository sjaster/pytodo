from enum import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class State(Enum):
    ACTIVE = 1
    DONE = 2

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    cards = db.relationship('Card', backref='user')

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    content = db.Column(db.Text())
    state = db.Column(db.Enum(State))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
