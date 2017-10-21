from flask import Flask, request, session, redirect, url_for, render_template, flash
from .db.database import Database

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='dev_key'))

database = Database()

@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    error = None

    if request.method == 'POST':
        entries = database.query_db('select username from users')
        for entry in entries:
            if request.form['user'] == entry['username']:
                error = 'User already taken'
                return render_template('register.html', error=error)
    
        db = database.get_db()
        db.execute('insert into users (username, hash) values (?, ?)',[request.form['user'], request.form['passwd']])
        db.commit()
        flash("Registration succesfull")
        return redirect(url_for('login', entries=entries))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if 'logged_in' in session:
        error = 'Already Logged in'
        return redirect(url_for('home', error=error))

    if request.method == 'POST':
        match = database.query_db('select * from users where username=?',[request.form['user']])
        if not match:
            error = 'Invalid username'
        else:
            for entry in match:
                if entry[2] != request.form['passwd']:
                    error = 'Invalid password'
                else:
                    session['logged_in']=True
                    session['username']=request.form['user']
                    flash('You were logged in')
                    return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))
