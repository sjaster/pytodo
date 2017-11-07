from flask import session, flash, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'logged_in' in session:
            flash('You need to be logged in to access this page!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            flash('You are already logged in!')
            return redirect(url_for('subject_overview'))
        return f(*args, **kwargs)
    return decorated_function
