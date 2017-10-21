import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, render_template, flash

app = Flask(__name__)

app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db/users.db'),
    SECRET_KEY='dev_key'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('users/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')



def connect_db():
    """Connects to the specific database."""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if not hasattr(g, 'db/users.db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db/users.db'):
        g.sqlite_db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    error = None

    if request.method == 'POST':
        entries = query_db('select username from users')
        for entry in entries:
            if request.form['user'] == entry['username']:
                error = 'User already taken'
                return render_template('register.html', error=error)
    
        db = get_db()
        db.execute('insert into users (username, hash) values (?, ?)',[request.form['user'], request.form['passwd']])
        db.commit()
        flash("Registration succesfull")
        return redirect(url_for('login', entries=entries))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        match = query_db('select * from users where username=?',[request.form['user']])
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
