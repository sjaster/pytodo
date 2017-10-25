from flask import Flask, request, session, redirect, url_for, render_template, flash, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4
from hashlib import sha256
from flask_migrate import Migrate
from .models import User, Card, Subject
from pytodo.models import db
from os import makedirs, path

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

@app.route('/cards', methods=['GET', 'POST'])
def cards():
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

    if 'logged_in' in session:
        if session['logged_in']:
            users = User.query.filter_by(username=session['username'])
            for user in users:
                user_id = user.id
            cards = Card.query.filter_by(user_id=user_id, state='ACTIVE')
            return render_template('cards.html', cards=cards)

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    error = None

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

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if 'logged_in' in session:
        flash('You are already logged in!')
        return redirect(url_for('subject_overview', error=error))

    if request.method == 'POST':
        try:
            match = User.query.filter_by(username=request.form['user']).one()
        except NoResultFound:
            error = 'Invalid Username'
            
        match = User.query.filter_by(username=request.form['user'])
        for entry in match:
            if check_passwd(entry.password, request.form['passwd']):
                error = 'Invalid password'
            else:
                session['logged_in']=True
                session['username']=request.form['user']
                flash('You were succesfully logged in!')
                return redirect(url_for('subject_overview'))

    return render_template('login.html', error=error)


def hash_passwd(passwd):
    salt = uuid4().hex
    return sha256(salt.encode() + passwd.encode()).hexdigest() + ":" + salt

def check_passwd(hashed_pw, passwd):
    password, salt = hashed_pw.split(":")
    return passwd == sha256(salt.encode() + passwd.encode()).hexdigest()

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/cards/create', methods=['GET', 'POST'])
def create_card():
    users = User.query.filter_by(username=session['username'])
    for user in users:
        user_id = user
    
    if request.method == 'POST':
        new_card = Card(title=request.form['title'], content=request.form['content'], state='ACTIVE', user_id=user_id.id, subject_id=request.form['subject_id'])
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('cards'))

    subjects = Subject.query.filter_by(user_id=user_id.id)

    return render_template('create_card.html', subjects=subjects)

@app.route('/')
def subject_overview():

    if session['logged_in']:
        users = User.query.filter_by(username=session['username'])
        for user in users:
            user_id = user.id
        subjects = Subject.query.filter_by(user_id=user_id)
        return render_template('index.html', subjects=subjects)

    return render_template('index.html')

@app.route('/subject/create', methods=['GET', 'POST'])
def create_subject():
    session['create_subject'] = True

    if request.method == 'POST':
        users = User.query.filter_by(username=session['username'])
        for user in users:
            user_id = user
        new_subject = Subject(name=request.form['subject'], user_id=user_id.id)
        db.session.add(new_subject)
        db.session.commit()
        session.pop('create_subject', None)
        
    return redirect(url_for('subject_overview'))
