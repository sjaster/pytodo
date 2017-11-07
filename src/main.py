from flask import request, session, redirect, url_for, render_template, flash, json
from .models import User, Card, Subject, Context
from .config import app, migrate, db, recaptcha
from .decorators import check_login, login_required
from os import makedirs, path


if not path.exists('/pytodo/db'):
    makedirs('/pytodo/db')

card_g = Card()
user_g = User()
subject_g = Subject()

@app.route('/register', methods=['GET','POST'])
@check_login
def register_user():
    error = None
    
    if request.method == 'POST':
        if recaptcha.verify():
            error = user_g.register(request.form['user'],request.form['passwd'])
            if error:
                return render_template('register.html', error=error, context=Context.register)
            flash('Registration succesull!')
            return redirect(url_for('login'))
        else:
            error = 'Please fill out the Captcha!'
            return render_template('register.html', error=error, context=Context.register)

    return render_template('register.html', context=Context.register)

@app.route('/login', methods=['GET', 'POST'])
@check_login
def login():
    error = None

    if request.method == 'POST':
        error = user_g.login(request.form['user'],request.form['passwd'])
        if not error:
            flash('You were succesfully logged in!')
            return redirect(url_for('subject_overview'))
            
    return render_template('login.html', error=error, context=Context.login)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    user = user_g.get_current_user()
    subjects = subject_g.get_subject_by_user(user.id)
    cards = card_g.get_active_cards_by_user(user.id)

    if request.method == 'POST':
        if 'card_id_del' in request.form.keys():
            card_g.delete(request.form['card_id_del'])

        elif 'card_id_archive' in request.form.keys():
            card_g.archive(request.form['card_id_archive'])            

        elif 'card_id' in request.form.keys():
            card_g.edit(request.form['card_id'],request.form['edit_title'],request.form['edit_content'],request.form['subject_id'])

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
        return render_template('cards.html', cards=search_cards, subjects=subjects, context=Context.card, request_path=request.path)

    return render_template('cards.html', cards=cards, subjects=subjects, context=Context.card, request_path=request.path)

@app.route('/cards/create', methods=['GET', 'POST'])
@login_required
def create_card():
    user = User().get_current_user()
    
    if request.method == 'POST':
        card_g.create(request.form['title'],request.form['content'],user.id,request.form['subject_id'])
        return redirect(url_for('cards'))

    if subject_g.get_subject_count(user.id) == 0:
        flash('You need to create a subject first!')
        return redirect(url_for('cards'))

    subjects = subject_g.get_subject_by_user(user.id)
    return render_template('create_card.html', subjects=subjects, context=Context.card_create)

@app.route('/', methods=['GET', 'POST'])
@login_required
def subject_overview():
    user = user_g.get_current_user()
    subjects = subject_g.get_subject_by_user(user.id)

    if request.method == 'POST':
        if 'subject_del' in request.form.keys():
            if request.form['confirm_delete'] == 'true':
                subject_g.delete(request.form['subject_del'])
        
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
        return render_template('index.html', subjects=search_subj, context=Context.subject, request_path=request.path)
    else:
        if 'create_subject' in session:
            return render_template('index.html', subjects=subjects, context=Context.subject_create)
        else:
            return render_template('index.html', subjects=subjects, context=Context.subject, request_path=request.path)

@app.route('/subject/create', methods=['GET', 'POST'])
@login_required
def create_subject():
    session['create_subject'] = True

    if request.method == 'POST':
        if 'subj_create' in request.form.keys():
            user = user_g.get_current_user()
            subject_g.create(request.form['subject'], user.id)
            session.pop('create_subject', None)

        elif 'subj_create_cancel' in request.form.keys():
            session.pop('create_subject', None)
        
    return redirect(url_for('subject_overview'))

@app.route('/<subject_name>/cards', methods=['GET', 'POST'])
@login_required
def cards_by_subject(subject_name):
    if request.method == 'POST':
        if 'card_id_del' in request.form.keys():
            card_g.delete(request.form['card_id_del'])

        elif 'card_id_archive' in request.form.keys():
            card_g.archive(request.form['card_id_archive'])

        elif 'card_id' in request.form.keys():
            card_g.edit(request.form['card_id'],request.form['edit_title'],request.form['edit_content'],request.form['subject_id'])

    user = user_g.get_current_user()
    subjects = subject_g.get_subject_by_user(user.id)

    subject = subject_g.get_single_subject(subject_name)
    cards = card_g.get_active_cards_by_subject(subject.id)
    return render_template('cards.html', cards=cards, context=Context.subject_single + subject.name, subject_name=subject.name, subjects=subjects, request_path=request.path)

@app.route('/<subject_name>/cards/create', methods=['GET', 'POST'])
@login_required
def create_card_by_subject(subject_name):
    user = user_g.get_current_user()

    if request.method == 'POST':
        card_g.create(request.form['title'], request.form['content'], user.id, request.form['subject_id'])
        return redirect(url_for('cards_by_subject', subject_name=subject_name))

    subjects = subject_g.get_subject_by_user(user.id)
    return render_template('create_card.html',subjects=subjects, subject_name=subject_name)

