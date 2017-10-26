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
    subjects = db.relationship('Subject', backref='user', lazy=True)
    cards = db.relationship('Card', backref='user', lazy=True)


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    state = db.Column(db.Enum(State))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cards = db.relationship('Card', backref='subjects', lazy=True, cascade='delete')
