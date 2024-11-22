from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    applied_for_teacher = BooleanField('Apply for Teacher Role')
    submit = SubmitField('Register')

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    headline_picture = FileField('Headline Picture')
    body = TextAreaField('Body', validators=[DataRequired()])
