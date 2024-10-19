from flask import Blueprint, render_template, flash, redirect, url_for, session, request, current_app
from .forms import LoginForm, RegistrationForm, ArticleForm
from .models import db, User, Article, Contact
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .decorators.auth_decorators import admin_required
import os


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
            if user.is_active:
                login_user(user)
                session['username'] = username
                session['role'] = user.role
                return redirect(url_for('main.dashboard'))
            else:
                flash('Your account has been temporarily blocked. Please contact support.', 'danger')
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

@main.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')
    role = session.get('role')  # Retrieve role from session
    return render_template("dashboard.html", username=username, role=role)

@main.route('/logout')
def logout():
    return redirect(url_for('main.index'))

@main.route('/admin/approve_teacher/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_teacher(user_id):
    user = User.query.get(user_id)
    if user:
        action = request.form.get('action')
        if action == 'approve':
            user.role = 'teacher'
            user.is_teacher_approved = True
            user.applied_for_teacher = False
        db.session.commit()
    else:
        flash('User not found or not applied for teacher', 'error')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/user_notification')
@login_required
@admin_required
def user_notification():
    try:
        users = User.query.filter(User.applied_for_teacher).all()
        return render_template('user_notification.html', users=users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return "An error occurred", 500

@main.route('/admin/users_list')
@login_required
@admin_required
def users_list():
    try:
        users = User.query.filter(User.role != 'admin').all()
        return render_template('users_list.html', users=users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return "An error occurred", 500

@main.route('/admin/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get(user_id)
    if user:
        action = request.form.get('action')
        if action == 'activate':
            user.is_active = True
        elif action == 'deactivate':
            user.is_active = False
        db.session.commit()
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/new_article', methods=['GET'])
@login_required
@admin_required
def new_article():
    form = ArticleForm()
    return render_template('create_article.html', form=form)

@main.route('/admin/create_article', methods=['POST'])
@login_required
@admin_required
def create_article():
    form = ArticleForm()
    if form.validate_on_submit():
        headline_picture = form.headline_picture.data
        if headline_picture:
            filename = secure_filename(headline_picture.filename)
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            headline_picture.save(os.path.join(uploads_dir, filename))

        article = Article(
            title=form.title.data,
            headline_picture=filename if headline_picture else None,
            body=form.body.data,
        )
        db.session.add(article)
        db.session.commit()
    else:
        return render_template('create_article.html', form=form)

    return redirect(url_for('main.dashboard'))
    
@main.route('/admin/articles_list')
@login_required
@admin_required
def articles_list():
    try:
        articles = Article.query.all()
        return render_template('articles_list.html', articles=articles)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return "An error occurred", 500

@main.route('/admin/toggle_article_status/<int:article_id>', methods=['POST'])
@login_required
@admin_required
def toggle_article_status(article_id):
    article = Article.query.get(article_id)
    if article:
        action = request.form.get('action')
        if action == 'activate':
            article.is_active = True
        elif action == 'deactivate':
            article.is_active = False
        db.session.commit()
    else:
        flash('Article not found.', 'danger')

    return redirect(url_for('main.dashboard'))

@main.route('/admin/edit_article/<int:article_id>', methods=['GET'])
@login_required
@admin_required
def render_edit_article(article_id):
    article = Article.query.get(article_id)
    if not article:
        flash('Article not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = ArticleForm()
    form.title.data = article.title
    form.body.data = article.body
    headline_picture = article.headline_picture if article.headline_picture else None

    return render_template('create_article.html', form=form, article_id=article_id, headline_picture=headline_picture)


@main.route('/admin/update_article/<int:article_id>', methods=['POST'])
@login_required
@admin_required
def update_article(article_id):
    article = Article.query.get(article_id)
    if not article:
        flash('Article not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = ArticleForm()

    if form.validate_on_submit():
        headline_picture = form.headline_picture.data
        if headline_picture:
            filename = secure_filename(headline_picture.filename)
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            headline_picture.save(os.path.join(uploads_dir, filename))
            article.headline_picture = filename

        article.title = form.title.data
        article.body = form.body.data
        db.session.commit()

        flash('Article updated successfully.', 'success')
    else:
        flash('Failed to update the article. Please check the form for errors.', 'danger')

    return redirect(url_for('main.dashboard'))

@main.route('/admin/contacts', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_contacts():
    contacts = Contact.query.all()
    return render_template('contacts.html', contacts=contacts)

@main.route('/admin/add_contacts', methods=['GET', 'POST'])
@login_required
@admin_required
def add_contacts():
    contact_types = request.form.getlist('contact_type[]')
    contact_values = request.form.getlist('contact_value[]')

    for contact_type, contact_value in zip(contact_types, contact_values):
        if contact_type and contact_value:
            new_contact = Contact(contact_type=contact_type, contact_value=contact_value)
            db.session.add(new_contact)

    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/admin/delete_contact/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/admin/statistics', methods=['GET'])
@login_required
@admin_required
def render_statistics():
    total_number_of_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    teachers = User.query.filter_by(is_teacher_approved=True).count()
    applied_for_teachers = User.query.filter_by(applied_for_teacher=True).count()

    users_with_active_courses = None

    total_courses = None
    active_courses = None
    courses_for_approval = None

    stats = {
        'total_users': total_number_of_users,
        'active_users': active_users,
        'teachers': teachers,
        'applied_for_teachers': applied_for_teachers,
        'users_with_active_courses': users_with_active_courses,
        'total_courses' : total_courses,
        'active_courses' : active_courses,
        'courses_for_approval' : courses_for_approval
    }

    return render_template('statistics.html', stats=stats)

@main.route('/home_content')
def home_content():
    return render_template('home_content.html')

@main.route('/blog_content')
def blog_content():
    articles = Article.query.filter_by(is_active=True).all()
    return render_template('blog_content.html', articles=articles)

@main.route('/article_detail/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article_detail.html', article=article)

@main.route('/contacts_content')
def contacts_content():
    contacts = Contact.query.all()
    return render_template('contacts_content.html', contacts=contacts)

@main.route('/under_construction')
def under_construction():
    return render_template('under_construction.html')