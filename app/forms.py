from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import Email, EqualTo, Length, DataRequired

class Registration(FlaskForm):
    username = StringField(label='Username', validators=[Length(min = 1, max = 40),  DataRequired()])
    email = EmailField(label='Email Address', validators=[Email("Not a valid email"),  DataRequired()])
    password = PasswordField(label="Password", validators=[Length(min = 1),  DataRequired()])
    confirm = PasswordField(label='Confirm Password', validators=[EqualTo("password"),  DataRequired()])
    submit = SubmitField(label='Register')

    # def validate_email(form, field):


class Login(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')
