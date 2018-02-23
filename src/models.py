from flask import session, flash
from enum import Enum
from uuid import uuid4
from hashlib import sha256
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, UnmappedInstanceError
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

    def hash_passwd(self, passwd):
        salt = uuid4().hex
        return sha256(salt.encode() + passwd.encode()).hexdigest() + ":" + salt

    def check_passwd(self, hashed_pw, passwd):
        password, salt = hashed_pw.split(":")
        return password == sha256(salt.encode() + passwd.encode()).hexdigest()

    def register(self, username, password):
        hashed_pw = self.hash_passwd(password)
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            return 'Username already taken!'
    
    def login(self, username, password):
        try:
            match = User.query.filter_by(username=username).one()
        except NoResultFound:
            return 'Invalid Username'

        if self.check_passwd(match.password, password):
            session['logged_in'] = True
            session['username'] = username
        else:
            return 'Invalid Password'

    def get_current_user(self):
        return User.query.filter_by(username=session['username']).one()

    def get_single_user(self, username):
        return User.query.filter_by(username=username).one()
        

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    state = db.Column(db.Enum(State))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    def create(self, title, content, user_id, subject_id):
        card = Card(title=title, content=content, state='ACTIVE', user_id=user_id, subject_id=subject_id)
        db.session.add(card)
        db.session.commit()

    def delete(self, card_id):
        Card.query.filter_by(id=card_id).delete()
        db.session.commit()

    def archive(self, card_id):
        card = Card.query.get(card_id)
        card.state = 'DONE'
        db.session.commit()

    def edit(self, card_id, title, content, subject_id):
        card = Card.query.get(card_id)
        card.title = title
        card.content = content
        card.subject_id = subject_id
        db.session.commit()

    def get_active_cards_by_user(self, user_id):
        return Card.query.filter_by(user_id=user_id, state='ACTIVE')

    def get_active_cards_by_subject(self, subject_id):
        return Card.query.filter_by(subject_id=subject_id)
    
    def search_cards(self, search, user_id):
        cards = self.get_active_cards_by_user(user_id)
        if search == '':
            search_cards = cards
        else:
            search_cards = []
            for card in cards:
                if str.lower(search) in str.lower(card.title):
                    search_cards.append(card)
        return search_cards

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cards = db.relationship('Card', backref='subjects', lazy=True, cascade='delete')

    def get_subject_by_user(self, user_id):
        return Subject.query.filter_by(user_id=user_id)

    def get_single_subject(self, name):
        return Subject.query.filter_by(name=name).one()

    def delete(self, subject_id):
        subject = db.session.query(Subject).filter_by(id=subject_id).first()
        try:
            db.session.delete(subject)
            db.session.commit()
        except:
            flash('This subject has already been deleted!')

    def create(self, name, user_id):
        new_subject = Subject(name=name, user_id=user_id)
        db.session.add(new_subject)
        db.session.commit()

    def get_subject_count(self, user_id):
        subjects = self.get_subject_by_user(user_id)
        count = 0
        for subject in subjects:
            count += 1
        return count

    def search_subjects(self, search, user_id):
        subjects = self.get_subject_by_user(user_id)
        if search == '':
            search_subj = subjects
        else:
            search_subj = []
            for subject in subjects:
                if str.lower(search) in str.lower(subject.name):
                    search_subj.append(subject)
        return search_subj

class Context:
    subject = 'Subject Overview'
    subject_single = 'Subject - '
    subject_create = 'Create new Subject'
    subject_search = 'Search Subjects'
    card = 'Card Overview'
    card_create = 'Create new Card'
    card_search = 'Search Cards'
    register = 'Pytodo Register'
    login = 'Pytodo Login'
    manage_user = 'management'
