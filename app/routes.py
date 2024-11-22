from flask import Blueprint, render_template, flash, redirect, url_for, session, request, current_app
from .forms import LoginForm, RegistrationForm, ArticleForm
from .models import db, User, Article, Contact, Course, UserCourse
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .decorators.auth_decorators import admin_required
from .enums import CourseStatus
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
                session['id'] = user.id
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
            flash('Username or email already exists.', 'danger')
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
    role = session.get('role')
    return render_template("dashboard.html", role=role, username=username)

@main.route('/logout')
def logout():
    logout_user()
    session.pop('username', None)
    session.pop('role', None)
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
    username = session.get('username')
    role = session.get('role')
    try:
        users = User.query.filter(User.applied_for_teacher).all()
        return render_template('user_notification.html', users=users, username=username, role=role)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return "An error occurred", 500

@main.route('/admin/users_list')
@login_required
@admin_required
def users_list():
    username = session.get('username')
    role = session.get('role')
    try:
        users = User.query.filter(User.role != 'admin').all()
        return render_template('users_list.html', users=users, username=username, role=role)
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
    return redirect(url_for('main.users_list'))

@main.route('/admin/new_article', methods=['GET'])
@login_required
@admin_required
def new_article():
    username = session.get('username')
    role = session.get('role')
    form = ArticleForm()
    return render_template('create_article.html', form=form, username=username, role=role)

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

    return redirect(url_for('main.articles_list'))
    
@main.route('/admin/articles_list')
@login_required
@admin_required
def articles_list():
    username = session.get('username')
    role = session.get('role')
    try:
        articles = Article.query.all()
        return render_template('articles_list.html', articles=articles, username=username, role=role)
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

    return redirect(url_for('main.articles_list'))

@main.route('/admin/edit_article/<int:article_id>', methods=['GET'])
@login_required
@admin_required
def render_edit_article(article_id):
    article = Article.query.get(article_id)
    if not article:
        flash('Article not found.', 'danger')
        return redirect(url_for('main.articles_list'))

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
        return redirect(url_for('main.articles_list'))

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

    return redirect(url_for('main.articles_list'))

@main.route('/admin/contacts', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_contacts():
    username = session.get('username')
    role = session.get('role')
    contacts = Contact.query.all()
    return render_template('contacts.html', contacts=contacts, username=username, role=role)

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
    return redirect(url_for('main.admin_contacts'))

@main.route('/admin/delete_contact/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
    return redirect(url_for('main.admin_contacts'))

@main.route('/admin/statistics', methods=['GET'])
@login_required
@admin_required
def render_statistics():
    username = session.get('username')
    role = session.get('role')

    total_number_of_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    teachers = User.query.filter_by(is_teacher_approved=True).count()
    applied_for_teachers = User.query.filter_by(applied_for_teacher=True).count()

    users_with_active_courses = (
        db.session.query(UserCourse.user_id)
        .filter(UserCourse.is_started == True)
        .distinct()
        .count()
    )
    active_courses = (
        db.session.query(UserCourse.course_id)
        .filter(UserCourse.is_started == True)
        .distinct()
        .count()
    )

    total_courses = Course.query.count()
    courses_for_approval = Course.query.filter_by(status=CourseStatus.SEND_FOR_REVIEW_AND_PUBLISHING).count()

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

    return render_template('statistics.html', stats=stats, username=username, role=role)

@main.route('/home_content')
def home_content():
    username = session.get('username')
    role = session.get('role')
    return render_template('home_content.html', username=username, role=role)

@main.route('/blog_content')
def blog_content():
    username = session.get('username')
    role = session.get('role')
    articles = Article.query.filter_by(is_active=True).all()
    return render_template('blog_content.html', articles=articles, username=username, role=role)

@main.route('/article_detail/<int:article_id>')
def article_detail(article_id):
    username = session.get('username')
    role = session.get('role')
    article = Article.query.get_or_404(article_id)
    return render_template('article_detail.html', article=article, username=username, role=role)

@main.route('/contacts_content')
def contacts_content():
    username = session.get('username')
    role = session.get('role')
    contacts = Contact.query.all()
    return render_template('contacts_content.html', contacts=contacts, username=username, role=role)

@main.route('/under_construction')
def under_construction():
    username = session.get('username')
    role = session.get('role')
    return render_template('under_construction.html', username=username, role=role)

@main.route("/teacher_statistics", methods=['GET', 'POST'])
def teacher_statistics():
    username = session.get('username')
    role = session.get('role')
    return render_template('under_construction.html', username=username, role=role)

@main.route("/teacher/create_course", methods=['GET', 'POST'])
@login_required
def create_course():
    username = session.get('username')
    role = session.get('role')
    return render_template('create_course.html', username=username, role=role)

@main.route("/save_course", methods=['GET', 'POST'])
@login_required
def save_course():
    if request.method == 'POST':
        course_title = request.form.get('courseTitle')
        course_intro = request.form.get('courseIntro')
        course_image = request.files.get('courseImage')
        author_id = session.get('id')

        if not course_title or not course_intro:
            flash('Title and Introduction are required.', 'error')
            return redirect(url_for('main.create_course'))

        if course_image:
            image_filename = secure_filename(course_image.filename)
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            course_image.save(os.path.join(uploads_dir, image_filename))
        else:
            image_filename = 'course_default_image.png'

        new_course = Course(
            title=course_title,
            headline_picture=image_filename,
            body=course_intro,
            status=CourseStatus.NOT_REVIEWED_NOT_PUBLISHED,
            author_id=author_id
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        flash('Course saved successfully!', 'success')

        return redirect(url_for('main.create_course'))
    
    username = session.get('username')
    role = session.get('role')
    return render_template('create_course.html', username=username, role=role)

@main.route("/teacher/author_courses", methods=['GET'])
@login_required
def author_courses():
    try:
        username = session.get('username')
        role = session.get('role')
        user_id = session.get('id')

        author_courses = Course.query.filter_by(author_id=user_id).all()

        return render_template('author_courses.html', author_courses=author_courses, username=username, role=role)
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return "An error occurred", 500

@main.route('/teacher/send_course_for_review/<int:course_id>', methods=['GET', 'POST'])
@login_required
def send_course_for_review(course_id):
    course = Course.query.get(course_id)
    if course:
        course.status = CourseStatus.SEND_FOR_REVIEW_AND_PUBLISHING
        db.session.commit()

    return redirect(url_for('main.author_courses'))

@main.route('/teacher/change_course_status_request/<int:course_id>', methods=['GET', 'POST'])
@login_required
def change_course_status_request(course_id):
    course = Course.query.get(course_id)
    if course:
        if course.status == CourseStatus.REVIEWED_PUBLISHED:
            course.status = CourseStatus.DISABEL_COURSE_REQUEST
        elif course.status == CourseStatus.DISABLED:
            course.status = CourseStatus.ENABLE_COURSE_REQUEST

        db.session.commit()

    return redirect(url_for('main.author_courses'))

# ToDo
@main.route('/teacher/edit_course/<int:course_id>')
def edit_course(course_id):
    username = session.get('username')
    role = session.get('role')
    return render_template('under_construction.html', username=username, role=role)

@main.route('/admin/courses_review', methods=['GET'])
@login_required
@admin_required
def courses_review():
    courses_for_review = Course.query.filter_by(status=CourseStatus.SEND_FOR_REVIEW_AND_PUBLISHING).all()

    username = session.get('username')
    role = session.get('role')
    return render_template('courses_for_approval.html', courses_for_review=courses_for_review, username=username, role=role)

@main.route('/admin/publish_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def publish_course(course_id):
    course = Course.query.get(course_id)

    if course:
        course.status = CourseStatus.REVIEWED_PUBLISHED
        db.session.commit()

    return redirect(url_for('main.courses_review'))

@main.route('/admin/available_courses_admin')
@login_required
@admin_required
def available_courses_admin():
    excluded_statuses = [
        CourseStatus.SEND_FOR_REVIEW_AND_PUBLISHING, 
        CourseStatus.NOT_REVIEWED_NOT_PUBLISHED
    ]
    available_courses = Course.query.filter(~Course.status.in_(excluded_statuses)).all()

    sorted_courses = sorted(
        available_courses,
        key=lambda course: course.status in [
            CourseStatus.DISABEL_COURSE_REQUEST, 
            CourseStatus.ENABLE_COURSE_REQUEST
        ],
        reverse=True
    )

    username = session.get('username')
    role = session.get('role')
    return render_template('available_courses_admin.html', available_courses=sorted_courses, username=username, role=role)

@main.route('/admin/toggle_courses_status/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def toggle_courses_status(course_id):
    course = Course.query.get(course_id)
    if course:
        if course.status == CourseStatus.REVIEWED_PUBLISHED:
            course.status = CourseStatus.DISABLED
        elif course.status == CourseStatus.DISABLED:
            course.status = CourseStatus.REVIEWED_PUBLISHED
        elif course.status == CourseStatus.DISABEL_COURSE_REQUEST:
            course.status = CourseStatus.DISABLED
        elif course.status == CourseStatus.ENABLE_COURSE_REQUEST:
            course.status = CourseStatus.REVIEWED_PUBLISHED

        db.session.commit()

    return redirect(url_for('main.available_courses_admin'))

@main.route('/course_details/<int:course_id>')
@login_required
def course_details(course_id):
    try:
        username = session.get('username')
        role = session.get('role')

        course = Course.query.get(course_id)

        return render_template('course_details.html', course=course, username=username, role=role)
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return "An error occurred", 500

@main.route('/available_courses')
def available_courses():
    included_with_status = [
        CourseStatus.REVIEWED_PUBLISHED,
        CourseStatus.DISABEL_COURSE_REQUEST
    ]

    available_courses = Course.query.filter(Course.status.in_(included_with_status)).all()

    is_logged_in = 'username' in session
    username = session.get('username') if is_logged_in else None
    role = session.get('role') if is_logged_in else None

    subscribed_courses = set()
    if is_logged_in:
        user_id = session.get('id')
        subscribed_courses = {
            uc.course_id for uc in UserCourse.query.filter_by(user_id=user_id, is_subscribed=True).all()
        }

    return render_template(
        'available_courses_global.html', 
        available_courses=available_courses,
        subscribed_courses=subscribed_courses, 
        is_logged_in=is_logged_in,
        username=username,
        role=role
        )

@main.route('/subscribe_to_course', methods=['POST'])
@login_required
def subscribe_to_course():
    try:
        course_id = request.form.get('course_id')
        if not course_id:
            flash("Course ID is missing.", "error")
            return redirect(url_for('main.available_courses'))

        course = Course.query.get(course_id)
        if not course:
            flash("Invalid course ID.", "error")
            return redirect(url_for('main.available_courses'))

        existing_subscription = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if existing_subscription:
            flash("You are already subscribed to this course.", "info")
            return redirect(url_for('main.available_courses'))

        user_course = UserCourse(
            user_id=current_user.id, 
            course_id=course_id, 
            is_subscribed=True
        )
        db.session.add(user_course)
        db.session.commit()

        flash("Successfully subscribed to the course!", "success")
        return redirect(url_for('main.available_courses'))

    except Exception as e:
        db.session.rollback()
        print(f"Error subscribing to course: {e}")
        flash("An error occurred while subscribing to the course. Please try again.", "error")
        return redirect(url_for('main.available_courses'))


@main.route('/my_courses')
@login_required
def my_courses():
    user_id_sess = session.get('id')
    if not user_id_sess:
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('main.login'))

    mycourses = UserCourse.query.filter_by(user_id=user_id_sess).all()

    username = session.get('username')
    role = session.get('role')

    return render_template('my_courses.html', mycourses=mycourses, username=username, role=role)

@main.route('/start_course/<int:course_id>', methods=['POST'])
@login_required
def start_course(course_id):
    try:
        user_course = UserCourse.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id
        ).first()

        if not user_course:
            return redirect(url_for('main.my_courses'))

        if user_course.is_started:
            return redirect(url_for('main.my_courses'))

        user_course.is_started = True
        db.session.commit()

        return redirect(url_for('main.course_chat', course_id=course_id))

    except Exception as e:
        db.session.rollback()
        print(f"Error starting course: {e}")
        return redirect(url_for('main.my_courses'))


#ToDo
@main.route('/continue_course/<int:course_id>')
@login_required
def continue_course(course_id):
    username = session.get('username')
    role = session.get('role')
    return redirect(url_for('main.course_chat', username=username, role=role))

#ToDo
@main.route('/course_chat/<int:course_id>')
@login_required
def course_chat(course_id):
    username = session.get('username')
    role = session.get('role')
    return render_template('course_chat.html', username=username, role=role)
