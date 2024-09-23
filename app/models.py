from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin', 'teacher' or 'student'
    is_active = db.Column(db.Boolean, default=True)
    applied_for_teacher = db.Column(db.Boolean, default=False)
    is_teacher_approved = db.Column(db.Boolean, default=False)