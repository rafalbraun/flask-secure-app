from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import Config
from models import User, db, bcrypt
from forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, RequestActivationForm
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/internal")
@login_required
def internal():
    return render_template('internal.html')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if not user.active:
            flash('Login Unsuccessful. Account is not active, please check your email box or resend activation email', 'info')
        else:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('request_reset.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)

@app.route("/request_activation", methods=['GET', 'POST'])
def request_activation():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestActivationForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user.active:
            flash('The account is already active.', 'info')
        else:
            send_activation_email(user)
            flash('An email has been sent with instructions to activate your account.', 'info')
        return redirect(url_for('login'))
    return render_template('request_activation.html', title='Request Activation', form=form)

@app.route("/resend_activation/<token>", methods=['GET', 'POST'])
def resend_activation(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_activation_token(token)
    if user is None:
        flash('That is an invalid or expired activation token', 'warning')
        return redirect(url_for('request_activation'))
    else:
        user.active = True
        db.session.commit()
        flash('Your account has been activated! You are now able to log in', 'success')
        return redirect(url_for('login'))

def send_reset_email(user):
    token = user.create_reset_token()
    url = url_for('reset_token', token=token, _external=True)
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.html = f'''
                To reset your password, visit the following link:<br>
                <a href="{url}">{url}</a><br><br>
                If you did not make this request then simply ignore this email and no changes will be made.
                '''
    mail.send(msg)

def send_activation_email(user):
    token = user.create_activation_token()
    url = url_for('resend_activation', token=token, _external=True)
    msg = Message('Account Activation Request', sender='noreply@demo.com', recipients=[user.email])
    msg.html = f'''
                To activate your account, visit the following link:<br>
                <a href="{url}">{url}</a><br><br>
                If you did not make this request then simply ignore this email and no changes will be made.
                '''
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
