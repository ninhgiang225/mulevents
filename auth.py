from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models import User
from forms import LoginForm, SignupForm
from flask_login import login_user, logout_user, login_required

bp = Blueprint('auth', __name__, template_folder='templates')

# manually copy paste CA email list here (since there is no administration interface yet)
VERIFIED_CA_EMAILS = set([
    'ngnguy26@colby.edu',
    'lnvuon28@colby.edu',
    'dkng28@colby.edu',
    'rriver28@colby.edu',
    'kmhers28@colby.edu',
    'jjoo27@colby.edu',
    'gdmaul28@colby.edu',
    'sdishw26@colby.edu',
    'rjpark26@colby.edu',
    'aaabde26@colby.edu',
    'hko26@colby.edu'
])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            
            return redirect(url_for("main.feed"))
        flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if form.email.data not in VERIFIED_CA_EMAILS:
            flash('Email not in CA list! If you are CA, please contact us to be added in the list; otherwise, you do not need to sign up', 'warning')
            return render_template('signup.html', form=form)
        hashed = generate_password_hash(form.password.data)
        user = User(name=form.name.data, 
                    email = form.email.data, 
                    password = hashed, 
                    is_ca = True, 
                    building=form.building.data, 
                    residents_count=form.residents_count.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html', form=form) 


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.feed'))
