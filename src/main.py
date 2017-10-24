from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
app.config.update(dict(SQLALCHEMY_DATABASE_URI='sqlite:////pytodo/db/db.sqlite3'))
db = SQLAlchemy(app)

app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='dev_key'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)

@app.cli.command('initdb')
def initdb_command():
    db.create_all(app=app)
    print('Initialized the database.')

@app.route('/test')
def design_test():
    return render_template('test.html')

@app.route('/')
def home():
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
