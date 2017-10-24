from flask import Flask, request, session, redirect, url_for, render_template, flash, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .models import User, Card
from pytodo.models import db

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='dev_key'))
app.config.update(dict(SQLALCHEMY_DATABASE_URI='sqlite:////pytodo/db/db.sqlite3'))
app.config.update(dict(SQLALCHEMY_TRACK_MODIFICATIONS='False'))

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    db.create_all(app=app)
    print('Initialized the database.')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # flash(request.form)
        card = Card.query.get(request.form['card_id'])
        card.title = request.form['edit_title']
        card.content = request.form['edit_content']
        db.session.commit()

    if session['logged_in']:
        users = User.query.filter_by(username=session['username'])
        for user in users:
            user_id = user.id
        cards = Card.query.filter_by(user_id=user_id)
        return render_template('index.html', cards=cards)

    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    error = None

    if request.method == 'POST':
        user = User(username=request.form['user'], password=request.form['passwd'])
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
        return redirect(url_for('home', error=error))

    if request.method == 'POST':
        try:
            match = User.query.filter_by(username=request.form['user']).one()
        except NoResultFound:
            error = 'Invalid Username'
            
        match = User.query.filter_by(username=request.form['user'])
        for entry in match:
            if request.form['passwd'] != entry.password:
                error = 'Invalid password'
            else:
                session['logged_in']=True
                session['username']=request.form['user']
                flash('You were succesfully logged in!')
                return redirect(url_for('home'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/create', methods=['GET', 'POST'])
def create_card():
    if request.method == 'POST':
        users = User.query.filter_by(username=session['username'])
        for user in users:
            user_id = user
        new_card = Card(title=request.form['title'], content=request.form['content'], state='ACTIVE', user_id=user_id.id)
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('create_card.html')
