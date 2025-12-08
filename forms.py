from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, IntegerField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_wtf.file import FileField, FileAllowed
from models import User


class LoginForm(FlaskForm): 
    email=StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    email=StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    building= StringField('Building hosted', validators=[DataRequired()])
    residents_count = IntegerField('Number of residents', validators=[DataRequired()])


class EventForm(FlaskForm):
    title = StringField('Event name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    collab_ca = SelectField("Collaborating CA (optional)", choices=[],  validate_choice=False, validators=[Optional()])
    event_type = SelectField('Type', choices=[('Community Gathering Program','Community Gathering Program'),('Hall Chat','Hall Chat'),('Barn Chat','Barn Chat'),('Mule Mindset Program','Mule Mindset Program')],validators=[DataRequired()])
    location = StringField('Where', validators=[DataRequired()])
    start_time = StringField('Start time', validators=[DataRequired()])
    end_time = StringField('End time', validators=[DataRequired()])
    image = FileField('Upload Poster', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')],description="Optional event poster")