from flask import Blueprint, render_template, flash, redirect, url_for, session
from .forms import LoginForm, RegistrationForm
from .models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required
from .decorators.auth_decorators import admin_required

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template("login.html", form=form)

@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        applied_for_teacher = form.applied_for_teacher.data
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists. Please choose another.', 'danger')
            return redirect(url_for('main.register'))
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            applied_for_teacher=applied_for_teacher
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template("register.html", form=form)

@main.route("/dashboard")
def dashboard():
    username = session.get('username')
    return render_template("dashboard.html", username=username)

@main.route('/logout')
def logout():
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/admin/approve_teacher/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_teacher(user_id):
    user = User.query.get(user_id)
    if user and user.applied_for_teacher:
        user.role = 'teacher'
        user.is_teacher_approved = True
        db.session.commit()
        flash('Teacher application approved', 'success')
    else:
        flash('User not found or not applied for teacher', 'error')
    return redirect(url_for('admin_dashboard'))
