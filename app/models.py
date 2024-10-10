from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


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

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    headline_picture = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_type = db.Column(db.String(100), nullable=False)
    contact_value = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Contact {self.contact_type}: {self.contact_value}>'