from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField,DateTimeField,IntegerField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError,Email,EqualTo,Length,number_range
from app.models import User

class LoginForm(FlaskForm):
    username =StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    passwordcheck = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Name already taken please reinput')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already taken please reinput')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0,max=140)])
    submit = SubmitField('Submit')

    def __init__(self,original_username,*args,**kwargs):
        super(EditProfileForm, self).__init__(*args,**kwargs)
        self.original_username = original_username

    def validate_username(self,username):
        if username.data!= self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('username already exists')

class PostForm(FlaskForm):
    title = TextAreaField('Title of project',validators=[
        DataRequired(),Length(min=1,max=100)])
    details = TextAreaField('project details', validators=[
        DataRequired(), Length(min=1, max=1000)])
    start_time = DateTimeField('expected date of project',format='%m/%d/%y %H:%M')
    max_participant = IntegerField('No of participants',validators=[
        DataRequired(number_range(min=1,max=100)) ])
    submit = SubmitField('Post')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    submit = SubmitField('Reset Password request')

