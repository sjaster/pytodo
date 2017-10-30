from flask import Flask, request, session, redirect, url_for, render_template, flash, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4
from hashlib import sha256
from flask_migrate import Migrate
from .models import User, Card, Subject, Context
from pytodo.models import db
from os import makedirs, path
from functools import wraps

if not path.exists('/pytodo/db'):
    makedirs('/pytodo/db')

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='dev_key'))
app.config.update(dict(SQLALCHEMY_DATABASE_URI='sqlite:////pytodo/db/db.sqlite3'))
app.config.update(dict(SQLALCHEMY_TRACK_MODIFICATIONS='False'))

migrate = Migrate(app, db)
db.init_app(app)
db.create_all(app=app)

context = Context()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'logged_in' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_passwd(passwd):
    salt = uuid4().hex
    return sha256(salt.encode() + passwd.encode()).hexdigest() + ":" + salt

def check_passwd(hashed_pw, passwd):
    password, salt = hashed_pw.split(":")
    return password == sha256(salt.encode() + passwd.encode()).hexdigest()

@app.route('/register', methods=['GET','POST'])
def register_user():
    error = None

    if 'logged_in' in session:
        flash('You already have an account!')
        return redirect(url_for('subject_overview'))

    if request.method == 'POST':
        hashed_pw = hash_passwd(request.form['passwd'])
        user = User(username=request.form['user'], password=hashed_pw)
        db.session.add(user)
        try: 
            db.session.commit()
        except IntegrityError:
            error='Username already taken!'
            return render_template('register.html', error=error)
        flash('Registration succesull!')
        return redirect(url_for('login'))

    return render_template('register.html', context=context.register)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if 'logged_in' in session:
        flash('You are already logged in!')
        return redirect(url_for('subject_overview'))

    if request.method == 'POST':
        try:
            match = User.query.filter_by(username=request.form['user']).one()
        except NoResultFound:
            error = 'Invalid Username'
            return render_template('login.html', error=error, context=context.login)

        if check_passwd(match.password, request.form['passwd']):
            session['logged_in'] = True
            session['username'] = request.form['user']
            flash('You were succesfully logged in!')
            return redirect(url_for('subject_overview'))
        else:
            error = 'Invalid password'

    return render_template('login.html', error=error, context=context.login)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    user = User.query.filter_by(username=session['username']).one()
    cards = Card.query.filter_by(user_id=user.id, state='ACTIVE')
    subjects = Subject.query.filter_by(user_id=user.id)

    if request.method == 'POST':
        if 'card_id_del' in request.form.keys():
            Card.query.filter_by(id=request.form['card_id_del']).delete()
            db.session.commit()

        elif 'card_id_archive' in request.form.keys():
            card = Card.query.get(request.form['card_id_archive'])
            card.state = 'DONE'
            db.session.commit()

        elif 'card_id' in request.form.keys():
            card = Card.query.get(request.form['card_id'])
            card.title = request.form['edit_title']
            card.content = request.form['edit_content']
            card.subject_id = request.form['subject_id']
            db.session.commit()

        if 'search' in request.form.keys():
            search = request.form['search']
            if search == '':
                search_cards = cards
            else:
                search_cards = []
                for card in cards:
                    if str.lower(search) in str.lower(card.title):
                        search_cards.append(card)
    
    if 'search' in request.form.keys():
        return render_template('cards.html', cards=search_cards, subjects=subjects, context=context.card, request_path=request.path)

    return render_template('cards.html', cards=cards, subjects=subjects, context=context.card, request_path=request.path)

@app.route('/cards/create', methods=['GET', 'POST'])
@login_required
def create_card():
    user = User.query.filter_by(username=session['username']).one()
    
    if request.method == 'POST':
        new_card = Card(title=request.form['title'], content=request.form['content'], state='ACTIVE', user_id=user.id, subject_id=request.form['subject_id'])
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('cards'))

    subjects = Subject.query.filter_by(user_id=user.id)
    return render_template('create_card.html', subjects=subjects, context=context.card_create)

@app.route('/', methods=['GET', 'POST'])
@login_required
def subject_overview():

    user = User.query.filter_by(username=session['username']).one()
    subjects = Subject.query.filter_by(user_id=user.id)

    if request.method == 'POST':
        if 'subject_del' in request.form.keys():
            subject = db.session.query(Subject).filter_by(id=request.form['subject_del']).first()
            db.session.delete(subject)
            db.session.commit()
        
        if 'search' in request.form.keys():
            search = request.form['search']
            if search == '':
                search_subj = subjects
            else:
                search_subj = []
                for subject in subjects:
                    if str.lower(search) in str.lower(subject.name):
                        search_subj.append(subject)
    
    if 'search' in request.form.keys():
        return render_template('index.html', subjects=search_subj, context=context.subject, request_path=request.path)
    else:
        if 'create_subject' in session:
            return render_template('index.html', subjects=subjects, context=context.subject_create)
        else:
            return render_template('index.html', subjects=subjects, context=context.subject, request_path=request.path)

@app.route('/subject/create', methods=['GET', 'POST'])
@login_required
def create_subject():
    session['create_subject'] = True

    if request.method == 'POST':
        if 'subj_create' in request.form.keys():
            user = User.query.filter_by(username=session['username']).one()
            new_subject = Subject(name=request.form['subject'], user_id=user.id)
            db.session.add(new_subject)
            db.session.commit()
            session.pop('create_subject', None)

        elif 'subj_create_cancel' in request.form.keys():
            session.pop('create_subject', None)
        
    return redirect(url_for('subject_overview'))

@app.route('/<subject_name>/cards', methods=['GET', 'POST'])
@login_required
def cards_by_subject(subject_name):
    if request.method == 'POST':
        if 'card_id_del' in request.form.keys():
            Card.query.filter_by(id=request.form['card_id_del']).delete()
            db.session.commit()

        elif 'card_id_archive' in request.form.keys():
            card = Card.query.get(request.form['card_id_archive'])
            card.state = 'DONE'
            db.session.commit()

        elif 'card_id' in request.form.keys():
            card = Card.query.get(request.form['card_id'])
            card.title = request.form['edit_title']
            card.content = request.form['edit_content']
            db.session.commit()

    user = User.query.filter_by(username=session['username']).one()
    subjects = Subject.query.filter_by(user_id=user.id)

    subject = Subject.query.filter_by(name=subject_name).one()
    cards = Card.query.filter_by(subject_id=subject.id)
    return render_template('cards.html', cards=cards, context=context.subject_single + subject.name, subject_name=subject.name, subjects=subjects, request_path=request.path)

@app.route('/<subject_name>/cards/create', methods=['GET', 'POST'])
@login_required
def create_card_by_subject(subject_name):
    user = User.query.filter_by(username=session['username']).one()

    if request.method == 'POST':
        new_card = Card(title=request.form['title'], content=request.form['content'],state='ACTIVE', user_id=user.id, subject_id=request.form['subject_id'])
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('cards_by_subject', subject_name=subject_name))

    subjects = Subject.query.filter_by(user_id=user.id)
    return render_template('create_card.html',subjects=subjects, subject_name=subject_name)

